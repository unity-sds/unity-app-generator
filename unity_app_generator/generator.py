import os
import sys
import tempfile
import logging
from glob import glob

from .state import ApplicationState
from .ecr_helper import ECRHelper

from app_pack_generator import GitManager, DockerUtil, ApplicationNotebook
from app_pack_generator import ProcessCWL, DataStagingCWL, Descriptor

from unity_sds_client.services.application_service import DockstoreAppCatalog

logger = logging.getLogger(__name__)

class ApplicationGenerationError(Exception):
    pass

class UnityApplicationGenerator(object):

    def __init__(self, state_directory, source_repository=None, destination_directory=None, checkout=None,
                 repo2docker_config=None, use_namespace=None, use_repository=None, use_tag=None):

        if not ApplicationState.exists(state_directory):
            self.repo_info = self._localize_source(source_repository, destination_directory, checkout)
            self.app_state = ApplicationState(state_directory, self.repo_info.directory, source_repository)
        else:
            self.app_state = ApplicationState(state_directory)
            self.repo_info = self._localize_source(self.app_state.source_repository, self.app_state.app_base_path, checkout)

        # Use value from command line to override values saved into app state
        image_namespace = use_namespace if use_namespace is not None else self.app_state.docker_image_namespace
        image_repository = use_repository if use_repository is not None else self.app_state.docker_image_repository
        image_tag = use_tag if use_tag is not None else self.app_state.docker_image_tag

        self.docker_util = DockerUtil(self.repo_info, do_prune=False,
                                      repo_config=repo2docker_config,
                                      use_namespace=image_namespace,
                                      use_repository=image_repository,
                                      use_tag=image_tag)

    def _localize_source(self, source, dest, checkout):

        # Check out original repository
        git_mgr = GitManager(source, dest)
    
        if checkout is not None:
            logger.info(f"Checking out {checkout} in {dest}")
            git_mgr.checkout(checkout)

        return git_mgr

    def create_docker_image(self):
 
        # These come either from the commandline or are generated by Docker util
        self.app_state.docker_image_namespace = self.docker_util.image_namespace
        self.app_state.docker_image_repository = self.docker_util.image_repository
        self.app_state.docker_image_tag = self.docker_util.image_tag

        # Create Docker image
        self.app_state.docker_image_reference = self.docker_util.build_image()

    def push_to_docker_registry(self, docker_registry):

        # Push to remote repository
        self.app_state.docker_url = self.docker_util.push_image(docker_registry, self.app_state.docker_image_reference)

    def push_to_aws_ecr(self):

        ecr_helper = ECRHelper(self.docker_util)

        # Create an ECR registry if it doesn't already exist
        ecr_helper.create_repository()

        # Log in to ECR via Docker
        registry_url = ecr_helper.docker_login()

        # Push docker image into ECR
        self.push_to_docker_registry(registry_url)

    def _generate_dockstore_cwl(self, cwl_output_path, target_cwl_filename):

        template = f"""
cwlVersion: v1.0

class: Workflow
doc: |
    Required Dockstore CWL file hosted workflows registered by unity_py.

steps:
step:
    run: {target_cwl_filename}
"""
        
        # Hard code file name because it is a hard coded re
        dockstore_cwl_filename = os.path.join(cwl_output_path, "Dockstore.cwl")
        with open(dockstore_cwl_filename, "w") as cwl_file:
            cwl_file.write(template.lstrip())

    def create_cwl(self, cwl_output_path=None, docker_url=None, monolithic=False):

        # Fall through using docker_image_reference if docker_url does not exist because no push has occurred
        # Or if docker_url is supplied as an argument use that
        if docker_url is None and self.app_state.docker_url is not None:
            docker_url = self.app_state.docker_url
        elif docker_url is None and self.app_state.docker_image_reference is not None:
            docker_url = self.app_state.docker_image_reference
        elif docker_url is None:
            raise ApplicationGenerationError("Cannot create CWL files when Docker image tag or URL has not yet been registered through building and/or pushing Docker image")
        
        # Use passed CWL output path and set to app state, or else
        # use existing value from application state
        if cwl_output_path is not None:
            self.app_state.cwl_output_path = cwl_output_path
        else:
            cwl_output_path = self.app_state.cwl_output_path

        if not os.path.exists(cwl_output_path):
            os.makedirs(cwl_output_path)
    
        notebook_filename = os.path.join(self.repo_info.directory, "process.ipynb")

        app = ApplicationNotebook(notebook_filename)

        logger.info("Parameters:\n" + app.parameter_summary())
            
        # Create CWL files depending on the mode of production
        cwl_generators = [ ProcessCWL(app) ]

        if monolithic:
            cwl_generators.append( DataStagingCWL(app) )

        files_created = []
        for cwl_gen in cwl_generators:
            files_created += cwl_gen.generate_all(cwl_output_path, dockerurl=docker_url)
        
        # Add the JSON descriptor file
        desc = Descriptor(app, self.repo_info)
        files_created.append(desc.generate_descriptor(cwl_output_path, docker_url))

        # Add Dockstore.cwl, point it to the appropriate entry point
        if monolithic:
            self._generate_dockstore_cwl(cwl_output_path, "workflow.cwl")
        else:
            self._generate_dockstore_cwl(cwl_output_path, "process.cwl")

    def notebook_parameters(self):

        notebook_filename = os.path.join(self.repo_info.directory, "process.ipynb")

        nb = ApplicationNotebook(notebook_filename)

        params_str = "Parsed Notebook Parameters:\n"
        params_str += nb.parameter_summary()

        return params_str

    def _find_existing_app(self, app_catalog, app_name):

        for app_info in app_catalog.application_list(for_user=True):
            if app_info.dockstore_info['mode'] and app_info.name == app_name:
                return app_info

    def push_to_application_registry(self, dockstore_api_url, dockstore_token):

        if self.app_state.cwl_output_path is None or not os.path.exists(self.app_state.cwl_output_path):
            raise ApplicationGenerationError("Can not register into application registry before CWL generation step")

        app_catalog = DockstoreAppCatalog(dockstore_api_url, dockstore_token) 

        app_name = self.repo_info.name
        cwl_param_files = glob(os.path.join(self.app_state.cwl_output_path, "*.cwl"))
        json_param_files = glob(os.path.join(self.app_state.cwl_output_path, "*.json"))

        print(json_param_files)

        if len(cwl_param_files) == 0:
            raise ApplicationGenerationError("No application package CWL files found")

        if len(json_param_files) == 0:
            raise ApplicationGenerationError("No JSON parameter file found")

        if (reg_app := self._find_existing_app(app_catalog, app_name)) is not None:

            # Upload updated JSON and CWL files
            reg_app = app_catalog.upload_files(reg_app, cwl_files=cwl_param_files, json_files=json_param_files)

        else:
            # Register a new application with the CWL and JSON files
            reg_app = app_catalog.register(app_name=app_name, cwl_files=cwl_param_files, json_files=json_param_files, publish=True)

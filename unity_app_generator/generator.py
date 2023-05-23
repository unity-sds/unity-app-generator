import os
import sys
import tempfile
import logging

from .state import ApplicationState

from app_pack_generator import GitManager, DockerUtil, AppNB

logger = logging.getLogger(__name__)

class ApplicationGenerationError(Exception):
    pass

class UnityApplicationGenerator(object):

    def __init__(self, state_directory, source_repository=None, destination_directory=None, checkout=None):

        if not ApplicationState.exists(state_directory):
            self.repo_info = self._localize_source(source_repository, destination_directory, checkout)
            self.app_state = ApplicationState(state_directory, self.repo_info.directory, source_repository)
        else:
            self.app_state = ApplicationState(state_directory)
            self.repo_info = self._localize_source(self.app_state.source_repository, self.app_state.app_base_path, checkout)

        self.docker_util = DockerUtil(self.repo_info, do_prune=False)

    def _localize_source(self, source, dest, checkout):

        # Check out original repository
        git_mgr = GitManager(source, dest)
    
        if checkout is not None:
            logger.debug(f"Checking out {checkout} in {repo_dir}")
            git_mgr.checkout(checkout)

        return git_mgr

    def create_docker_image(self):

        # Create Docker image
        self.app_state.docker_image_tag = self.docker_util.repo2docker()

    def push_to_docker_registry(self, docker_registry, image_tag=None):

        if image_tag is not None:
            self.app_state.docker_image_tag = image_tag
        
        if self.app_state.docker_image_tag is None:
            raise ApplicationGenerationError("Cannot push Docker image to registry without a valid tag. Run the Docker build command or supply an image tag as an argument.")

        # Push to remote repository
        self.app_state.docker_url = self.docker_util.push_image(docker_registry, self.app_state.docker_image_tag)

    def create_cwl(self, cwl_output_path=None, docker_url=None):

        # Fall through using docker_image_tag if docker_url does not exist because no push has occurred
        # Or if docker_url is supplied as an argument use that
        if docker_url is None and self.app_state.docker_url is not None:
            docker_url = self.app_state.docker_url
        elif docker_url is None and self.app_state.docker_image_tag is not None:
            docker_url = self.app_state.docker_image_tag
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

        nb = AppNB(self.repo_info)
        files = nb.Generate(cwl_output_path, docker_url)

    def push_to_application_registry(self, dockstore_api):
        pass

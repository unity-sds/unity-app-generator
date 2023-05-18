import os
import sys
import tempfile
import logging

from app_pack_generator import GitManager, DockerUtil, AppNB

logger = logging.getLogger()

class UnityApplicationGenerator(object):

    def __init__(self, source, build_dir=None, checkout=None):

        self.build_dir = self._setup_build_directory(build_dir)
        self.checkout = checkout

        self.repo_info = self._localize_source(source, checkout)

        self.cwl_dir = os.path.realpath(os.path.join(self.build_dir, "cwl"))

        self.docker_util = DockerUtil(self.repo_info, do_prune=False)

    def _setup_build_directory(self, build_dir=None):

        if build_dir is None:
            build_dir = tempfile.gettempdir()

        logger.debug(f"Using directory {build_dir} as build directory for application temporary files")

        if not os.path.exists(build_dir):
            logger.debug(f"Build directory {build_dir} does not exist, creating")
            os.makedirs(build_dir)

        return build_dir

    def _localize_source(self, source, checkout):

        if os.path.exists(source):
            dest = None
            logger.debug(f"Using existing directory {source} for source repository")
        else:
            dest = os.path.realpath(os.path.join(build_dir, "application_repo"))
            logger.debug(f"Checking out {source} to {dest}")

        # Check out original repository
        git_mgr = GitManager(source, dest)
    
        if self.checkout is not None:
            logger.debug(f"Checking out {checkout} in {repo_dir}")
            git_mgs.checkout(checkout)

        return git_mgr

    def create_docker_image(self):

        # Create Docker image
        self.docker_util.repo2docker()

    def push_to_docker_registry(self, docker_registry):

        # Push to remote repository
        return self.docker_util.push_image(docker_registry)

    def create_cwl(self, docker_url):

        # Generate CWL artifacts within the output directory.
        if not os.path.exists(self.cwl_dir):
            os.makedirs(self.cwl_dir)

        nb = AppNB(self.repo_info)
        files = nb.Generate(self.cwl_dir, docker_url)

    def push_to_application_registry(self, dockstore_api):
        pass

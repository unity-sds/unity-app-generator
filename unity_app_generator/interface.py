"""
Provides a programmatic interface mirroring the command line interface of build_ogc_app
"""

DEFAULT_STATE_DIRECTORY = ".unity_app_gen"

import os
import logging

from unity_app_generator.generator import UnityApplicationGenerator, ApplicationGenerationError

logger = logging.getLogger()

# Defaulty name of place where application generation state data is kept
DEFAULT_STATE_DIRECTORY = ".unity_app_gen"

def state_directory_path(state_directory=None, destination_directory=None):
    "Resolve a path to the state directory based on which arguments are provided"

    if state_directory is not None:
        return os.path.realpath(state_directory)
    
    if destination_directory is not None:
        return os.path.realpath(os.path.join(destination_directory, DEFAULT_STATE_DIRECTORY))

    return os.path.realpath(os.path.join(os.curdir, DEFAULT_STATE_DIRECTORY))

def check_state_directory(state_dir):
    "Check that the application state directory exists"

    if not os.path.exists(state_dir):
        raise ApplicationGenerationError(f"Application state directory {state_dir} does not exist, please run init sub-command first")

    return state_dir

def init(state_directory, source_repository, destination_directory=None, checkout=None, **kwargs):
    "Initialize a Git repository for use by subsequent commands"

    state_dir = state_directory_path(state_directory, destination_directory)

    app_gen = UnityApplicationGenerator(state_dir, source_repository, destination_directory, checkout)

    return app_gen

def build_docker(state_directory, image_namespace=None, image_repository=None, image_tag=None, config_file=None, **kwargs):
    "Build a Docker image from the initialized application directory"

    state_dir = check_state_directory(state_directory_path(state_directory))

    app_gen = UnityApplicationGenerator(state_dir,
                                        repo2docker_config=config_file,
                                        use_namespace=image_namespace,
                                        use_repository=image_repository,
                                        use_tag=image_tag)

    app_gen.create_docker_image()

    return app_gen

def push_docker(state_directory, container_registry, **kwargs):
    state_dir = check_state_directory(state_directory_path(state_directory))

    app_gen = UnityApplicationGenerator(state_dir)

    app_gen.push_to_docker_registry(container_registry)

    return app_gen

def push_ecr(state_directory, **kwargs):
    state_dir = check_state_directory(state_directory_path(state_directory))

    app_gen = UnityApplicationGenerator(state_dir)

    app_gen.push_to_aws_ecr()

    return app_gen

def notebook_parameters(state_directory, **kwargs):

    state_dir = check_state_directory(state_directory_path(state_directory))

    app_gen = UnityApplicationGenerator(state_dir)

    print()
    print(app_gen.notebook_parameters())

    return app_gen

def build_cwl(state_directory, cwl_output_path=None, image_url=None, monolithic=False, **kwargs):
    state_dir = check_state_directory(state_directory_path(state_directory))

    app_gen = UnityApplicationGenerator(state_dir)

    app_gen.create_cwl(cwl_output_path=cwl_output_path, docker_url=image_url, monolithic=monolithic)

    return app_gen

def push_app_registry(state_directory, dockstore_api_url, dockstore_token, **kwargs):
    state_dir = check_state_directory(state_directory_path(state_directory))

    app_gen = UnityApplicationGenerator(state_dir)

    app_gen.push_to_application_registry(dockstore_api_url, dockstore_token)

    return app_gen
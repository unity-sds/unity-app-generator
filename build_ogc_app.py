#!/usr/bin/env python3
# 
# *** Unity Application Package Generator ***
#
# Builds an OGC compliant appplication using the Unity application interface.
# A Papermill parameterized Jupyter notebook is introspected to determine
# input and output paramters that are connected through CWL. This software uses
# the app-pack-generator as well as Unity.py.
#
# This software performs the following steps:
# * Builds a Docker image using repo2docker 
# * Pushes the Docker image into a container registry
# * Creates CWL files from application metadata and Docker registry URL
# * Register application and pushes CWL files into Dockstore

STATE_DIRECTORY = ".unity_app_gen"

import os
import logging
from argparse import ArgumentParser

from unity_app_generator.generator import UnityApplicationGenerator, ApplicationGenerationError

logger = logging.getLogger()

class SubCommandError(Exception):
    pass

def state_directory_path(args):

    if args.state_directory is not None:
        return os.path.realpath(args.state_directory)

    if hasattr(args, "destination_directory") and args.destination_directory is not None:
        return os.path.realpath(os.path.join(args.destination_directory, STATE_DIRECTORY))

    if hasattr(args, "source_repository") and os.path.isdir(args.source_repository):
        return os.path.realpath(os.path.join(args.source_repository, STATE_DIRECTORY))

    return os.path.realpath(os.path.join(os.curdir, STATE_DIRECTORY))

def check_state_directory(state_dir):

    if not os.path.exists(state_dir):
        raise SubCommandError(f"Application state directory {state_dir} does not exist, please run init sub-command first")

    return state_dir

def init(args):
    state_dir = state_directory_path(args)

    app_gen = UnityApplicationGenerator(state_dir, args.source_repository, args.destination_directory, args.checkout)

def build_docker(args):
    state_dir = check_state_directory(state_directory_path(args))

    app_gen = UnityApplicationGenerator(state_dir)

    app_gen.create_docker_image()

def push_docker(args):
    state_dir = check_state_directory(state_directory_path(args))

    app_gen = UnityApplicationGenerator(state_dir)
    
    app_gen.push_to_docker_registry(args.container_registry, image_tag=args.image_tag)

def build_cwl(args):
    state_dir = check_state_directory(state_directory_path(args))

    app_gen = UnityApplicationGenerator(state_dir)

    app_gen.create_cwl(cwl_output_path=args.cwl_output_path, docker_url=args.image_url)

def push_app_registry(args):
    pass

def main():
    parser = ArgumentParser(description="Unity Application Package Generator")

    parser.add_argument("--state_directory",
        help=f"An alternative location to store the application state other than {STATE_DIRECTORY}")

    # init
    subparsers = parser.add_subparsers(required=True)

    parser_init = subparsers.add_parser('init',
        help=f"Initialize a Git repository for use by this application. Creates a {STATE_DIRECTORY} directory in the destination directory")

    parser_init.add_argument("source_repository", 
        help="Directory or Git URL of application source files, default is current directory")

    parser_init.add_argument("destination_directory", nargs="?",
        help="Directory where to check out source repository, default is a directory under the current subdirectory with same basename as the source_repository")

    parser_init.add_argument("-c", "--checkout", required=False,
        help="Git hash, tag or branch to checkout from the source repository")

    parser_init.set_defaults(func=init)

    # build_docker

    parser_build_docker = subparsers.add_parser('build_docker',
        help=f"Build a Docker image from the initialized application directory")

    parser_build_docker.set_defaults(func=build_docker)

    # push_docker

    parser_push_docker = subparsers.add_parser('push_docker',
        help=f"Push a Docker image from the initialized application directory to a remote registry")

    parser_push_docker.add_argument("container_registry", 
        help="URL or Dockerhub username of a Docker registry for pushing of the built image")

    parser_push_docker.add_argument("-t", "--image_tag", 
        help="Docker image tag to push into container registry if already built without using the build_docker subcommand")

    parser_push_docker.set_defaults(func=push_docker)

    # create_cwl

    parser_build_cwl = subparsers.add_parser('build_cwl',
        help=f"Create OGC compliant CWL files from the repository and Docker image")

    parser_build_cwl.add_argument("-o", "--cwl_output_path", 
        help="Alternate location to place CWL output files other than within application state directory")

    parser_build_cwl.add_argument("-u", "--image_url", 
        help="Docker image tag or remote registry URL to be included in the generated CWL files if not using the build_docker and/or push_docker subcommands") 

    parser_build_cwl.set_defaults(func=build_cwl)

    # Process arguments

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    try:
        args.func(args)
    except (SubCommandError, ApplicationGenerationError) as err:
        parser.error(err)


    #app_gen.push_to_application_registry(None)

if __name__ == '__main__':
    main()

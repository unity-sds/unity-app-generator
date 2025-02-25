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

import logging
from argparse import ArgumentParser

from unity_app_generator.generator import ApplicationGenerationError

from . import interface

logger = logging.getLogger()

def main():
    parser = ArgumentParser(description="Unity Application Package Generator")

    parser.add_argument("--state_directory",
        help=f"An alternative location to store the application state other than {interface.DEFAULT_STATE_DIRECTORY}")

    parser.add_argument("--verbose", "-v", action="store_true", default=False,
        help=f"Enable verbose logging")

    # init
    subparsers = parser.add_subparsers(required=True)

    parser_init = subparsers.add_parser('init',
        help=f"Initialize a Git repository for use by this application. Creates a {interface.DEFAULT_STATE_DIRECTORY} directory in the destination directory")

    parser_init.add_argument("source_repository",
        help="Directory or Git URL of application source files, default is current directory")

    parser_init.add_argument("destination_directory", nargs="?",
        help="Directory where to check out source repository, default is a directory under the current subdirectory with same basename as the source_repository")

    parser_init.add_argument("-c", "--checkout", required=False,
        help="Git hash, tag or branch to checkout from the source repository")

    parser_init.set_defaults(func=interface.init)

    # build_docker

    parser_build_docker = subparsers.add_parser('build_docker',
        help=f"Build a Docker image from the initialized application directory")

    parser_build_docker.add_argument("-n", "--image_namespace", 
        help="Docker image namespace to use instead of the automatically generated one from the Git repository owner. An empty string removes the namespace from the image reference.")

    parser_build_docker.add_argument("-r", "--image_repository", 
        help="Docker image repository to use instead of the automatically generated one from the Git repository name.")

    parser_build_docker.add_argument("-t", "--image_tag", 
        help="Docker image tag to use instead of the automatically generated one from the Git commit id")

    parser_build_docker.add_argument("-c", "--config_file",
        help="JSON or Python Traitlets style config file for repo2docker. Use 'repo2docker --help-all' to see configurable options.")

    parser_build_docker.set_defaults(func=interface.build_docker)

    # push_docker

    parser_push_docker = subparsers.add_parser('push_docker',
        help=f"Push a Docker image from the initialized application directory to a remote registry")

    parser_push_docker.add_argument("container_registry", 
        help="URL or Dockerhub username of a Docker registry for pushing of the built image")

    parser_push_docker.set_defaults(func=interface.push_docker)

    # push_ecr

    parser_push_ecr = subparsers.add_parser('push_ecr',
        help=f"Push a Docker image from the initialized application directory to an AWS Elastic Container Registry (ECR)")

    parser_push_ecr.set_defaults(func=interface.push_ecr)

    # notebook_parameters

    parser_parameters = subparsers.add_parser('parameters',
        help=f"Display parsed notebook parameters")

    parser_parameters.set_defaults(func=interface.notebook_parameters)

    # build_cwl

    parser_build_cwl = subparsers.add_parser('build_cwl',
        help=f"Create OGC compliant CWL files from the repository and Docker image")

    parser_build_cwl.add_argument("-o", "--cwl_output_path", 
        help="Alternate location to place CWL output files other than within application state directory")

    parser_build_cwl.add_argument("-u", "--image_url", 
        help="Docker image tag or remote registry URL to be included in the generated CWL files if not using the build_docker and/or push_docker subcommands") 

    parser_build_cwl.add_argument("--monolithic", action="store_true",
        help="Use the deprecated 'monolithic' approach to generating CWL where stage in and out are bundled inside the application")

    parser_build_cwl.set_defaults(func=interface.build_cwl)

    # push_app_registry

    parser_app_registry = subparsers.add_parser('push_app_registry',
        help=f"Push CWL files to Dockstore application registry")

    parser_app_registry.add_argument("--api_url", dest="dockstore_api_url", required=True,
        help="Dockstore API URL including the trailing api/ portion of the URL") 

    parser_app_registry.add_argument("--token", dest="dockstore_token", required=True,
        help="Dockstore API token obtained from the My Services / Account page") 

    parser_app_registry.set_defaults(func=interface.push_app_registry)

    # Process arguments

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    try:
        args.func(**vars(args))
    except ApplicationGenerationError as err:
        parser.error(err)

if __name__ == '__main__':
    main()
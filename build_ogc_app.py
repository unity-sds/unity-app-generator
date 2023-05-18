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

from unity_app_generator.generator import UnityApplicationGenerator

logger = logging.getLogger()

def main():

    parser = ArgumentParser(description="Unity Application Package Generator")

    parser.add_argument("source_repository", 
        help="Directory or Git URL of application source files")

    parser.add_argument("-b", "--build_directory", required=False,
        help="Location where temporary files are staged, if not supplied a system temporary directory is used")

    parser.add_argument("-c", "--checkout", required=False,
        help="Git hash, tag or branch to checkout from the source repository")

    parser.add_argument("--container_registry", required=False,
        help="URL to a Docker registry for pushing of the built image")

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    app_gen = UnityApplicationGenerator(args.source_repository, args.build_directory, args.checkout)

    app_gen.create_docker_image()

    if args.container_registry is not None:
        docker_url = app_gen.push_to_docker_registry(args.container_registry)
    else:
        docker_url = app_gen.docker_util.image_tag

    app_gen.create_cwl(docker_url)

    app_gen.push_to_application_registry(None)

if __name__ == '__main__':
    main()

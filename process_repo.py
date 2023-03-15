import os
import sys

from app_pack_generator import GitHelper, DockerUtil, AppNB

def main(args):

    # Performs the following steps:
    # * Pushes a copy of source Git repo into Unity Gitlab for storage
    # * Builds a Docker image using repo2docker 
    # * Pushes Docker image into a container registry
    # * Creates CWL files from application metadata and Docker registry URL
    # * Register application with Dockstore
    # * Submits CWL files to Dockstore

    source_repo = args[1]
    build_dir = args[2]

    repo_dir = os.path.realpath(os.path.join(build_dir, "application_repo"))
    cwl_dir = os.path.realpath(os.path.join(build_dir, "cwl"))

    # Check out original repository
    repo = GitHelper(source_repo, dst=repo_dir)
    #repo.Checkout(checkout)
    os.chdir(repo_dir)

    # Create Docker image
    docker_util = DockerUtil(repo, do_prune=False)
    image_tag = docker_util.Repo2Docker()
    dockerurl = image_tag
    #dockerurl = docker_util.PushImage(image_tag, docker_registry)

    # Generate CWL artifacts within the output directory.
    if not os.path.exists(cwl_dir):
        os.makedirs(cwl_dir)

    nb = AppNB(repo)
    files = nb.Generate(cwl_dir, dockerurl)

    return_code = 0

    return return_code

if __name__ == '__main__':
    ret = main(sys.argv)

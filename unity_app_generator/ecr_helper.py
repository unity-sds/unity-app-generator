import base64

import boto3
from botocore.exceptions import ClientError

import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app_pack_generator import DockerUtil

logger = logging.getLogger(__name__)

class ECRHelper(object):

    def __init__(self, docker_util : 'DockerUtil'):

        self.docker_util = docker_util
        self.ecr_client = boto3.client("ecr")

    def create_repository(self):

        if self.docker_util.image_namespace is not None and self.docker_util.image_namespace != "":
            aws_repo_name = f"{self.docker_util.image_namespace}/{self.docker_util.image_repository}"
        else:
            aws_repo_name = self.docker_util.image_repository

        logger.info(f"Creating AWS ECR repository named: {aws_repo_name}")
        
        try:
            response = self.ecr_client.create_repository(
                repositoryName=aws_repo_name,
            )

            return response["repository"]['repositoryUri']

        except ClientError as err:
            if err.response["Error"]["Code"] == "RepositoryAlreadyExistsException":
                logger.debug(f"Repository {aws_repo_name} already exists.")
                response = self.ecr_client.describe_repositories(
                    repositoryNames=[aws_repo_name]
                )
                
                return response['repositories'][0]['repositoryUri']
            else:
                logger.error(
                    "Error creating repository %s. Here's why %s",
                    repository_name,
                    err.response["Error"]["Message"],
                )
                raise

    def docker_login(self):

        logger.info("Logging into Docker using ECR credentials")

        token = self.ecr_client.get_authorization_token()
        username, password = base64.b64decode(token['authorizationData'][0]['authorizationToken']).decode().split(':')

        # Remove the protocol prefix for this to work
        # https://github.com/docker/docker-py/issues/2256
        registry = token['authorizationData'][0]['proxyEndpoint'].replace("https://", "")

        response = self.docker_util.docker_client.login(
            username=username,
            password=password,
            registry=registry
        )

        return registry
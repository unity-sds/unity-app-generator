#!/bin/sh
printenv

echo "starting docker"
# Start Docker engine
dockerd &> dockerd-logfile &

# Wait until Docker engine is running
# Loop until 'docker version' exits with 0.
until docker version > /dev/null 2>&1
do
  sleep 1
  cat dockerd-logfile 
done

. /usr/share/apg/venv/bin/activate

echo "dockerhub username is"
echo $DOCKERHUB_USERNAME

echo $DOCKERHUB_TOKEN | docker login --username $DOCKERHUB_USERNAME --password-stdin

build_ogc_app init $GITHUB_REPO build
cd build
# unset DOCKER_HOST
build_ogc_app build_docker --no_owner

build_ogc_app push_docker $DOCKERHUB_USERNAME 
build_ogc_app build_cwl
build_ogc_app push_app_registry --api_url http://awslbdockstorestack-lb-1429770210.us-west-2.elb.amazonaws.com:9998/api --token $DOCKSTORE_TOKEN 

deactivate

# Stop Docker engine
pkill -f dockerd
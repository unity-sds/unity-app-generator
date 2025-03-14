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

echo "activating python environment"
. /usr/share/apg/venv/bin/activate

echo $DOCKER_PAT | docker login --username $DOCKER_USER --password-stdin

build_ogc_app init $GITHUB_REPO build
cd build
# unset DOCKER_HOST
build_ogc_app build_docker --no_owner

build_ogc_app push_docker $DOCKER_USER 
build_ogc_app build_cwl
build_ogc_app push_app_registry --api_url http://awslbdockstorestack-lb-1429770210.us-west-2.elb.amazonaws.com:9998/api --token $DOCKSTORE_TOKEN 

deactivate

# Stop Docker engine
pkill -f dockerd
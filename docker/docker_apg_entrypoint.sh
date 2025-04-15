#!/bin/sh

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

# This will not display the token to the logs 
echo $DOCKERHUB_TOKEN | docker login --username $DOCKERHUB_USERNAME --password-stdin

build_ogc_app init $GITHUB_REPO build
cd build
build_ogc_app build_docker --image_namespace ""

build_ogc_app push_docker $DOCKERHUB_USERNAME 
build_ogc_app build_cwl
build_ogc_app push_app_registry --api_url $DOCKSTORE_API_URL --token $DOCKSTORE_TOKEN 

deactivate

# Stop Docker engine
pkill -f dockerd
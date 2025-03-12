FROM docker:latest


# Input arguments from the user 
ARG SOURCE_REPO
ARG DOCKSTORE_API_URL="http://awslbdockstorestack-lb-1429770210.us-west-2.elb.amazonaws.com:9998/api"
ARG DOCKER_USERNAME
ARG MDPS_APP_GEN_VERSION=1.0.0

# Get the dockstore token and docker password from secrets 
RUN --mount=type=secret,id=dockstore_token,env=DOCKSTORE_TOKEN \
    --mount=type=secret,id=docker_password,env=DOCKER_PASSWORD

RUN python3 -m venv venv
RUN . venv/bin/activate && pip install mdps-app-generator==$MDPS_APP_GEN_VERSION
#RUN pip install mdps-app-generator==$MDPS_APP_GEN_VERSION

RUN docker login --username ${DOCKER_USERNAME} --password $DOCKER_PASSWORD

RUN . venv/bin/activate && build_ogc_app init $SOURCE_REPO alg-source-repo
# check this line is right 
RUN cd alg-source-repo
# make sure this works right 
RUN if [ "$MDPS_APP_GEN_VERSION" = 1.0.0 ]; then echo "version was 1.0.0" ; else echo "version was not 1.0.0"

RUN . venv/bin/activate && if [ "$MDPS_APP_GEN_VERSION" = 1.0.0 ]; then build_ogc_app build_docker --no_owner ; else build_ogc_app build_docker --image_namespace ""
RUN . venv/bin/activate && build_ogc_app push_docker $DOCKER_USERNAME
RUN . venv/bin/activate && build_ogc_app build_cwl
RUN . venv/bin/activate && build_ogc_app push_app_registry --api_url $DOCKSTORE_API_URL --token $DOCKSTORE_TOKEN
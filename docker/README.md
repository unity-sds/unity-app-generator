## Build the container

docker build . -t apg:0.3.1

## Execute

```
docker run --privileged --env GITHUB_REPO=https://github.com/mike-gangl/unity-OGC-example-application --env DOCKER_USER=JOHNDOE --env DOCKER_PAT=**** --env DOCKSTORE_TOKEN=**** apg:0.3.1 
```

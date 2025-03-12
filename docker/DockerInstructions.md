# Running Unity app gen
`docker buildx build --platform linux/amd64 --no-cache -t unity-app-gen --build-arg SOURCE_REPO=<source repo link> --build-arg DOCKSTORE_TOKEN=<token> -f docker/Dockerfile .`
Example of source repo link: https://github.com/unity-sds/unity-example-application

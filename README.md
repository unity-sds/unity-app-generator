<!-- Header block for project -->
<hr>

<div align="center">

![logo](https://user-images.githubusercontent.com/3129134/163255685-857aa780-880f-4c09-b08c-4b53bf4af54d.png)

<h1 align="center">Unity Application Generator</h1>
<!-- ☝️ Replace with your repo name ☝️ -->

</div>

<pre align="center">Creates and registers a Unity OGC application package</pre>

<!-- Header block for project -->

[app-pack-generator](https://github.com/unity-sds/app-pack-generator) | [unity-example-application](https://github.com/unity-sds/unity-example-application)

## Features

* Uses [app-pack-generator](https://github.com/unity-sds/app-pack-generator) to create CWL, application descriptor and Docker image
* Can output Jupyter noteboook parameterization for debugging purposes
* Pushes generated Docker image to a Docker registry
* Pushes generated application package files to a Dockstore application registry


## Requirements

* [app-pack-generator](https://pypi.org/project/app-pack-generator/)
* [Unity-py](https://pypi.org/project/unity-sds-client/)

## Setup Instructions

### Install from PyPi

```
pip install mdps-app-generator
```

## Usage

Unity application generation is accomplished by using the `build_ogc_app` program. It uses a stateful architecture such as in other programs such as ``git`` where actions on a repository can be done in a series of steps. These steps are listed when running `build_ogc_app --help`.

```
usage: build_ogc_app [-h] [--state_directory STATE_DIRECTORY] {init,build_docker,push_docker,parameters,build_cwl,push_app_registry} ...

Unity Application Package Generator

positional arguments:
  {init,build_docker,push_docker,parameters,build_cwl,push_app_registry}
    init                Initialize a Git repository for use by this application. Creates a .unity_app_gen directory in the destination directory
    build_docker        Build a Docker image from the initialized application directory
    push_docker         Push a Docker image from the initialized application directory to a remote registry
    parameters          Display parsed notebook parameters
    build_cwl           Create OGC compliant CWL files from the repository and Docker image
    push_app_registry   Push CWL files to Dockstore application registry

options:
  -h, --help            show this help message and exit
  --state_directory STATE_DIRECTORY
                        An alternative location to store the application state other than .unity_app_gen
```

By default a state directory name `.unity_app_gen` is created in the repository the tool is targeting. Usually this is within the repository directory itself unless the `--state_directory` argument is used. This directory contains metadata information and generated files created by steps and needed for subsequent steps.

### init

Before using the tool with a repository the state directory needs to be initialized:

```
usage: build_ogc_app init [-h] [-c CHECKOUT] source_repository [destination_directory]

positional arguments:
  source_repository     Directory or Git URL of application source files, default is current directory
  destination_directory
                        Directory where to check out source repository, default is a directory under the current subdirectory with same basename as the
                        source_repository

options:
  -h, --help            show this help message and exit
  -c CHECKOUT, --checkout CHECKOUT
                        Git hash, tag or branch to checkout from the source repository
```

This can be accomplished with an existing clone of a repository or the tool can clone the repository locally for you. If no directory is supplied the tool will assume you would like to initialize the current directory. When working interatively it is suggested to change to the directory you are working with and use the script from there. This simplifies program usage and does not require you to use the `--state_directory` argument on each call. 

For example to initialize an repository and use it locally:

```
git clone https://github.com/unity-sds/unity-example-application.git
cd unity-example-application
build_ogc_app init
```

Or to have the tool clone and initialize the repository for you:

```
build_ogc_app init https://github.com/unity-sds/unity-example-application.git unity-example-application
cd unity-example-application
```

### build_docker

The `build_docker` command does not require any additional arguments. It will utilize [app-pack-generator](https://github.com/unity-sds/app-pack-generator) and [repo2docker](https://github.com/jupyterhub/repo2docker), please see the documentation there for how to set up your repository for a successful build. The built Docker image name will be stored into `app_state.json` file in the state directory. This command requires the `init` step to have already been run.

### push_docker

This command will push a Docker image built by the `build_docker` step to a remote Docker registry. It will then record the remote registry URL into the state directory for use by subsequent steps. The `push_docker` command has a required argument of either the URL of a remote Docker registry or a Dockerhub username. It is assumed you have already used `docker login` to initialze credentials. This command requires the `build_docker` step to have already been run.

### build_cwl

The `build_cwl` will use [app-pack-generator](https://github.com/unity-sds/app-pack-generator) to create OGC compliant CWL files based on the parameterization of the Jupyter notebook in the target repository. Currently the Jupyter notebook is required to be named `process.ipynb`. Please see the [app-pack-generator](https://github.com/unity-sds/app-pack-generator) documentation for how to properly parameterize a notebook. The generated CWL files and application descriptor will be placed in the state directory. If the `push_docker ` step has not yet been run the CWL files will refer to the local Docker image tag instead a remote URL.

### push_app_registry

The `push_app_registry` command pushes the generated CWL into a Dockstore application registry server. It requires the the URL to the Dockstore API as well as a token obtained through the Dockstore interface. The `build_cwl` step is required to have already been executed.

```
usage: build_ogc_app push_app_registry [-h] --api_url DOCKSTORE_API_URL --token DOCKSTORE_TOKEN

options:
  -h, --help            show this help message and exit
  --api_url DOCKSTORE_API_URL
                        Dockstore API URL including the trailing api/ portion of the URL
  --token DOCKSTORE_TOKEN
                        Dockstore API token obtained from the My Services / Account page
```

The API URL can be obtained from the Dockstore user interface by scrolling to the bottom and clicking the API link in the footer. It will be the portion of the URL up to the `/api` path. The API token is obtained by logging into the Dockstore, clocking on the username drop down in the top right corner then selecting the Account item. Copy the token from the Dockstore Account item.

## Changelog

See our [CHANGELOG.md](CHANGELOG.md) for a history of our changes.

See our [releases page](https://github.com/unity-sds/unity-app-generator/releases) for our key versioned releases.

## License

See our: [LICENSE](LICENSE.txt)

# umd-handle-django

[Django]-based web application providing a REST-based Handle back-end service
with administrative user interface.

## Introduction

This application provides:

* a REST backend for resolving Handle.Net Registry handles to URLs.
* a REST-based API interface for administering handle to URL mappings
* an HTTP-based user interface for administering handle to URL mappings

Additional documentation for this application is in the "docs/" subdirectory,
including:

* [OpenAPI v3 Spec](docs/umd-handle-open-api-v1.yml)

## Development Environment Setup

* [Local Development Environment Setup](docs/DevelopmentEnvironmentLocal.md)

## Building the Docker Image for local testing

To build and run locally

```zsh
# Build
docker build --no-cache -t docker.lib.umd.edu/umd-handle-django:latest .

# Run
docker run -it \
-e DATABASE_URL=sqlite:///db.sqlite3 \
-e DEBUG=True \
-e SECRET_KEY=$(uuidgen | shasum -a 256 | cut -c-64) \
-e SERVER_PORT=3000 \
-p 3000:3000 \
docker.lib.umd.edu/umd-handle-django:latest
```

## Building the Docker Image for K8s Deployment

The following procedure uses the Docker "buildx" functionality and the
Kubernetes "build" namespace to build the Docker image. This procedure should
work on both "arm64" and "amd64" MacBooks.

The image will be automatically pushed to the Nexus.

### Local Machine Setup

See
<https://github.com/umd-lib/devops/blob/main/k8s/docs/guides/DockerBuilds.md> in
GitHub for information about setting up a MacBook to use the Kubernetes
"build" namespace.

### Creating the Docker image

1. In an empty directory, checkout the Git repository and switch into the
   directory:

    ```zsh
    git clone git@github.com:umd-lib/umd-handle-django.git
    cd umd-handle-django
    ```

2. Checkout the appropriate Git tag, branch, or commit for the Docker image.

3. Set up an "APP_TAG" environment variable:

    ```zsh
    export APP_TAG=<DOCKER_IMAGE_TAG>
    ```

   where \<DOCKER_IMAGE_TAG> is the Docker image tag to associate with the
   Docker image. This will typically be the Git tag for the application version,
   or some other identifier, such as a Git commit hash. For example, using the
   Git tag of "1.0.0":

    ```zsh
    export APP_TAG=1.0.0
    ```

    Alternatively, to use the Git branch and commit:

    ```zsh
    export GIT_BRANCH=`git rev-parse --abbrev-ref HEAD`
    export GIT_COMMIT_HASH=`git rev-parse HEAD`
    export APP_TAG=${GIT_BRANCH}-${GIT_COMMIT_HASH}
    ```

4. Switch to the Kubernetes "build" namespace:

    ```bash
    kubectl config use-context build
    ```

5. Create the "docker.lib.umd.edu/umd-handle-django" Docker image:

    ```bash
    docker buildx build --no-cache --platform linux/amd64 --push --no-cache \
        --builder=kube  -f Dockerfile -t docker.lib.umd.edu/umd-handle-django:$APP_TAG .
    ```

   The Docker image will be automatically pushed to the Nexus.

[Django]: https://www.djangoproject.com/

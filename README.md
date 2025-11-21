# umd-handle-django

[Django]-based web application providing a REST-based Handle back-end service
with administrative user interface.

## Introduction

This application provides:

* a REST backend for resolving Handle.Net Registry handles to URLs.
* a REST-based API interface for administering handle to URL mappings
* an HTTP-based user interface for administering handle to URL mappings

Additional documentation for this application is in the "[docs/](docs/)"
subdirectory, including:

* [Architecture Decision Records](docs/adr/)
* [OpenAPI v3 Spec](docs/umd-handle-open-api-v1.yml)
* [Test Plan](docs/TestPlan.md)

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

## Django Management Tasks

### CSV Import

#### Handles import

Entries from the "handles" table of the Rails-based "umd-handle" application
can be imported using the "db_import_handles_from_csv" management command:

```zsh
src/manage.py db_import_handles_from_csv <CSV_FILE>
```

where \<CSV_FILE> is a CSV file of entries to load. Existing entries in the
Django database that have matching prefix/suffix entries will be updated from
the CSV file.

A "--dry-run" option is available to determine the number of entries that would
be added, updated, or are invalid.

#### JWT Tokens import

Entries from the "jwt_token_logs" table of the Rails-based "umd-handle"
application can be imported using the "db_import_jwt_tokens_from_csv" management
command:

```zsh
src/manage.py db_import_jwt_tokens_from_csv <CSV_FILE>
```

where \<CSV_FILE> is a CSV file of entries to load. Existing entries in the
Django database that have matching token will be updated from the CSV file.

A "--dry-run" option is available to determine the number of entries that would
be added, updated, or are invalid.

### JWT Tokens

A list of JWT Tokens that have been issued by the system are stored in the
"JWTToken" model.

The "JWTToken" model is only designed to be a record of issued tokens, to
help identify which servers need to be updated if the tokens need to be
invalidated. The "JWTToken" model plays no role in validating tokens.

#### Create a JWT token for authorizing access to the REST API

```zsh
src/manage.py jwt_create_token "<DESCRIPTION>"
```

where \<DESCRIPTION> is a description of the server/service that will use the
token.

#### List JWT tokens

```zsh
src/manage.py jwt_list_tokens
```

## REST API

The REST API is specified in the OpenAPI v3.0 format:

* v1: [docs/umd-handle-open-api-v1.yml](docs/umd-handle-open-api-v1.yml)

## License

See the [LICENSE.md](LICENSE.md) file for license rights and limitations
(Apache 2.0).

---
[Django]: https://www.djangoproject.com/

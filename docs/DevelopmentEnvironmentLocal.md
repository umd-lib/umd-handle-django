# Development Environment - Local

## Introduction

This document provides guidance on setting up a umd-handle Django development
environment on a local workstation.

## Prerequisites

* Python 3.14

* Install `libxmlsec1`. This is required for the SAML authentication using
  [djangosaml2].

  On Mac, it is available via Homebrew:

  ```zsh
  brew install xmlsec1
  ```

  On Debian or Ubuntu Linux, it is available via `apt`:

  ```zsh
  sudo apt-get install xmlsec1
  ```

* Update the `/etc/hosts` file to add:

  ```zsh
  127.0.0.1 handle-local
  ```

## Application Setup

1) Clone umd-handle-django from GitHub:

    ```zsh
    git clone git@github.com:umd-lib/umd-handle-django.git
    cd umd-handle-django
    ```

2) Set up the Python virtual environment, and install the dependencies

    ```zsh
    python -m venv .venv
    source .venv/bin/activate
    pip install -e '.[test]'
    ```

3) Download the `handle-test-sp.key` and `handle-test-sp.crt` files from the
   "handle-test-saml" entry in LastPass into the project rooo directory.

    ℹ️ Note: These files can be placed in an directory outside the project,
    if desired. Also, when downloading the `handle-test-sp.crt`
    file, Google Chrome will modify the file extension, by default, to ".cer".
    Be sure to to specify the ".crt" extension when downloading the file.
    Mozilla Firefox preserves the ".crt" extension.

4) Copy the "env_example" file to ".env":

    ```zsh
    cp env_example .env
    ```

    and update the following variables with the appropriate values:

    * SAML_KEY_FILE - relative (or absolute) file path to the
      `handle-test-sp.key` file
    * SAML_CERT_FILE - relative (or absolute) file path to the
      ``handle-test-sp.crt` file
    * SECRET_KEY - Either comment out (a random key will be automatically
      generated), or populate with anything with sufficient randomness,
      i.e. `uuidgen | shasum -a 256 | cut -c-64`
    * XMLSEC1_PATH - The full file path to the "xmlsec1" binary, (usually
      findable by running `which xmlsec1`)

5) Initialize the database:

    ```zsh
    ./src/manage.py migrate
    ```

6) Create an administrative user:

   ```zsh
   ./src/manage.py createsuperuser
   ```

7) Run the application. The default port is 3000; this is also the port that
   is registered with DIT to allow SAML authentication to work from local:

    ```zsh
    ./src/manage.py runserver
    ```

    The application will be running at <http://handle-local:3000/>

    ----

    ℹ️ **Note:** When running locally with Rails applications (such as Archelon)
    that also run on port 3000, the port should be changed using an
    argument, i.e.:

    ```zsh
    ./src/manage.py runserver 3001
    ```

    When running on a different port the admin GUI will not be accessible,
    as it will not be possible to login via CAS. The backend API (which uses
    JWT tokens), will be available.

    ----

    The administrative interface is accessible at
    <http://handle-local:3000/admin>.

## Tests

This project uses [pytest] in conjunction with the [pytest-django] plugin
to run its tests. To run the test suite:

```zsh
pytest
```

To run with coverage information:

```zsh
pytest --cov src --cov-report term-missing
```

## Linter

This project uses [ruff] to lint and format the code.

To run the linter:

```zsh
ruff check
```

[djangosaml2]: https://djangosaml2.readthedocs.io/
[pytest]: https://pytest.org/
[pytest-django]: https://pytest-django.readthedocs.io/en/latest/
[ruff]: https://github.com/astral-sh/ruff
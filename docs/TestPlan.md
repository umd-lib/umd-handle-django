# Test Plan

## Introduction

This document provides a basic UMD Handle test plan that verifies as many
features and other concerns (such as functionality when using read-only
containers) as feasible.

The intention is to provide basic assurance that the application works as
expected, and guard against regressions.

As this test plan adds, modifies, and deletes data, it should ***not*** be used
to test the production system.

These tests are intended to be comprehensive (covering all functionality), but
*not* exhaustive (i.e., not all search possibilities or error paths are tested).

## Test Plan Assumptions

This test plan assumes that the user has "administrator" privileges, and can
log in via CAS.

The test plan steps are specified using URLs for the Kubernetes "sandbox"
namespace, as that seems to be the most useful. Unless otherwise specified,
test steps should work in the local development environment as well.

## UMD Handle Tests

The following verifies the operation of the UMD Handle API, as described in the
[docs/umd-handle-open-api-v1.yml](umd-handle-open-api-v1.yml) OpenAPI
specification.

### 1\) Setup the environment variables

1.1) Create a "K8S_NAMESPACE" environment variable for the Kubernetes namespace
being tested:

```zsh
$ export K8S_NAMESPACE=sandbox
```

1.2) Get the name of the "umd-handle-app" deployment pod, and store it in a
"K8S_HANDLE_APP_POD" environment variable:

```zsh
$ export K8S_HANDLE_APP_POD=$(kubectl get pods --selector=app=umd-handle-app --output=jsonpath='{.items[0].metadata.name}')
```

1.3) Create a "UMD_HANDLE_SERVER_URL" environment variable to store the URL
of the UMD Handle server:

```zsh
export UMD_HANDLE_SERVER_URL=https://handle.sandbox.lib.umd.edu
```

### 2\) umd-handle-app - JWT Token Creation

2.1) Switch to the Kubernetes namespace:

```zsh
$ kubectl config use-context $K8S_NAMESPACE
```

2.2) Run a Bash shell in the "umd-handle-app" deployment

```zsh
$ kubectl exec -it $K8S_HANDLE_APP_POD -- bash
```

2.3) Create a JWT token to use for testing:

```bash
umd-handle-app$ src/manage.py jwt_create_token "umd-handle test plan"
```

Note the output - it will be referred to as \<JWT_TOKEN> in the following steps.

2.4) List the JWT tokens:

```bash
umd-handle-app$ src/manage.py jwt_list_tokens
```

Verify that the JWT token added in the previous steps in the list.

2.5) Exit the Bash shell:

```bash
umd-handle-app$ <Ctrl-D>
```

2.6) Create a "UMD_HANDLE_JWT_TOKEN" environment variable using the JWT token
created in the previous step:

```zsh
$ export UMD_HANDLE_JWT_TOKEN=<JWT_TOKEN>
```

### 3\) UMD Handle API - Mint a new Handle

3.1) Attempt to mint a new handle without a JWT token by running the following
"curl" command:

```zsh
$ curl --silent --write-out "\n%{http_code}\n" -X POST \
  -H "Content-Type: application/json" \
  $UMD_HANDLE_SERVER_URL/api/v1/handles \
  -d '{"prefix": "1903.1", "url": "http://example.com/test", "repo": "fedora2", "repo_id": "test-123"}'
```

and verify that the output is:

```zsh
{"error": "Authentication required"}
401
```

3.2) Attempt to mint a new handle with an invalid JWT token by running the
following "curl" command:

```zsh
$ curl --silent --write-out "\n%{http_code}\n" -X POST \
  -H "Authorization: Bearer INVALID_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  $UMD_HANDLE_SERVER_URL/api/v1/handles \
  -d '{"prefix": "1903.1", "url": "http://example.com/test", "repo": "fedora2", "repo_id": "test-123"}'
```

and verify that the output is:

```zsh
{"error": "Invalid token"}
401
```

3.3) Attempt to mint a new handle with a JWT token an invalid parameters by
running the following "curl" command:

```zsh
$ curl  -X POST  --write-out "\n%{http_code}\n" \
  -H "Authorization: Bearer ${UMD_HANDLE_JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  $UMD_HANDLE_SERVER_URL/api/v1/handles \
  -d '{"prefix": "INVALID_PREFIX", "url": "http://example.com/test", "repo": "INVALID_REPO", "repo_id": "test-123"}'
```

and verify that the output is:

```zsh
{"errors": ["Value 'INVALID_PREFIX' is not a valid choice.", "Value 'INVALID_REPO' is not a valid choice."]}
400
```

3.4) Mint a new handle with a JWT token by running the following "curl" command:

```zsh
$ curl -X POST --write-out "\n%{http_code}\n" \
  -H "Authorization: Bearer ${UMD_HANDLE_JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  $UMD_HANDLE_SERVER_URL/api/v1/handles \
  -d '{"prefix": "1903.1", "url": "http://example.com/test", "repo": "fedora2", "repo_id": "test-123"}'
```

and verify that the output is similar to:

```zsh
{"suffix": "1", "handle_url": "https://hdl.sandbox.lib.umd.edu/1903.1/1", "request": {"prefix": "1903.1", "repo": "fedora2", "repo_id": "test-123", "url": "http://example.com/test"}}
200
```

Note: The "suffix" value, with will be referred to as  \<SUFFIX_VALUE> in the
following steps.

3.5) Create a "HANDLE_SUFFIX" environment variable, using the "suffix" (without
the quotes) from the previous step:

```zsh
$ export HANDLE_SUFFIX=<SUFFIX_VALUE>
```

### 4\) UMD Handle API - Retrieve a handle

4.1) Retrieve the handle using the "prefix/suffix" format using the following
"curl" command:

```zsh
$ curl -X GET --write-out "\n%{http_code}\n" \
  -H "Authorization: Bearer ${UMD_HANDLE_JWT_TOKEN}"  \
  -H "Content-Type: application/json" \
  $UMD_HANDLE_SERVER_URL/api/v1/handles/1903.1/$HANDLE_SUFFIX
```

and verify that the output is:

```zsh
{"url": "http://example.com/test"}
200
```

4.2) Retrieve the handle using the "exists" endpoint using the following
"curl" command:

```zsh
$ curl -X GET --write-out "\n%{http_code}\n" \
  -H "Authorization: Bearer ${UMD_HANDLE_JWT_TOKEN}"  \
  -H "Content-Type: application/json" \
  "$UMD_HANDLE_SERVER_URL/api/v1/handles/exists?repo=fedora2&repo_id=test-123"
```

and verify that the output is similar to:

```zsh
{"exists": true, "handle_url": "https://hdl.sandbox.lib.umd.edu/1903.1/1", "prefix": "1903.1", "suffix": "1", "url": "http://example.com/test", "request": {"repo": "fedora2", "repo_id": "test-123"}}
200
```

4.3) Retrieve the handle using the "info" endpoint using the following "curl"
command:

```zsh
$ curl -X GET --write-out "\n%{http_code}\n" \
  -H "Authorization: Bearer ${UMD_HANDLE_JWT_TOKEN}"  \
  -H "Content-Type: application/json" \
  "$UMD_HANDLE_SERVER_URL/api/v1/handles/info?prefix=1903.1&suffix=$HANDLE_SUFFIX"
```

and verify that the output is similar to:

```zsh
{"exists": true, "handle_url": "https://hdl.sandbox.lib.umd.edu/1903.1/1", "repo": "fedora2", "repo_id": "test-123", "url": "http://example.com/test", "request": {"prefix": "1903.1", "suffix": "1"}}
200
```

### 5\) UMD Handle API - Update a handle

5.1) Modify the repository id to "test-123-modified" by running the following
"curl" command:

```zsh
$ curl -X PATCH --write-out "\n%{http_code}\n" \
  -H "Authorization: Bearer ${UMD_HANDLE_JWT_TOKEN}"  \
  -H "Content-Type: application/json" \
  "$UMD_HANDLE_SERVER_URL/api/v1/handles/1903.1/$HANDLE_SUFFIX" \
  -d '{"repo_id": "test-123-modified"}'
```

and verify that the output is similar to the following:

```zsh
{"handle_url": "https://hdl.sandbox.lib.umd.edu/1903.1/1", "request": {"prefix": "1903.1", "repo": "fedora2", "repo_id": "test-123-modified", "url": "http://example.com/test"}}
200
```

## 6\) Handle.net Server Test

**Note:** This step cannot be tested in the local development environment.

A Handle.net handle server runs alongside the "umd-handle" application, and
communicates it via the REST API.

To verify the communication:

6.1) In a web browser, go to:

* sandbox - <https://hdl.sandbox.lib.umd.edu/>
* test - <https://hdl-test.lib.umd.edu/>
* qa - <https://hdl-qa.lib.umd.edu/>
* prod - <https://hdl.lib.umd.edu/>

A "Handle.net" page will be displayed.

6.2) On the "Handle.net" page, fill out the following fields

* Handle - the prefix/suffix of the handle added in the previous steps (using
  the example above, `1903.1/1`
* Left-click the "Don't Redirect to URLs" checkbox to select it

then left-click the "Submit" button.

Verify the a Handle.net page is displayed showing a table with the URL for
the handle displayed in the "Data" column (i.e., from the above example, the
"Data" column would display `http://example.com/test`).

### 7\) UMD Handle Website - robots.txt/sitemap.xml

**Note:** This step cannot be tested in the local development environment.

7.1) In a web browser, go to

<https://handle.sandbox.lib.umd.edu/robots.txt>

Verify that a robots.txt file is displayed that disallows all crawling.

7.2) In a web browser, go to

<https://handle.sandbox.lib.umd.edu/sitemap.xml>

Verify that either an empty page is returned (Chrome) or a page indicating an
XML Parsing error (Firefox) is returned.

### 8\) UMD Handle Website - Home page

8.1) In a web browser, go to

<https://handle.sandbox.lib.umd.edu/>

After logging in, the Django administration dashboard is displayed.

8.2) On the Django administration dashboard, verify that:

* the UMD favicon is displayed in the browser tab, and that the text in the
  browser tab is "UMD Handle Service Admin Portal | UMD Handle Service"
* the site title in the navigation bar is "UMD Handle Service"
* the page title below the navigation bar is "UMD Handle Service Admin Portal"
* that below the page title is an "API" section that only lists "Handles"
* that a "Users" and "Groups" entry in a "Authentication and Authorization"
  section is *not* displayed

8.3) On the "UMD Handle Service Admin Portal" page, left-click the "Handles"
entry. The "Select handle to change" page will be displayed.

8.4) On the "Select handle to change" page, verify that:

* there is a search textbox and a "Search" button
* A table listing all the handles, sorted by "Modified" date, in descending
  order (i.e.,  newest first), with the following fields:

  * Handle (displaying the combined prefix/suffix, i.e. "1903.1/13632"
    as a hyperlink)
  * Url (as a hyperlink)
  * Repo
  * Repo Id
  * Modified

* In the right sidebar there is a "Filter" panel, that allows filtering by:
  * Repo
  * Created
  * Modified

8.5) Left-click the "Handle" header in the table. Verify that the handles are
sorted in ascending order (since all the prefixes are the same, this will
be the lowest suffix at the top).

8.6) Left-click the "Handle" header in the table again and verify that the
handles are sorted in descending order (since all the prefixes are the
same, this will be the highest suffix at the top).

### 9\) UMD Handle Website - "Change handle" page

9.1) On the "Select handle to change" page, left-click the "Handle" field for
any entry. The "Change handle" page will be displayed.

9.2) On the "Change handle" page, verify that:

* the following fields are read-only and cannot be edited:

  * Prefix
  * Suffix
  * Created
  * Modified

* The "Repo" field displays as a drop-down list box.

9.3) Change the "Repo Id" field to something distinctive, such as
`TEST-TEST-TEST` and left-click the "Save" button. The
"Select handle to change" page will be displayed with a notification that the
handle was successfully changed.

Verify in the handle table that the handle entry was updated.

### 10\) UMD Handle Website - "Add handle" page

10.1) On the "Select handle to change" page, left-click the "Add Handle" button to
the right of the page title. The "Add handle" page will be displayed.

10.2) On the "Add handle" page, verify that:

* The "Prefix", and "Repo" fields display as drop-down list boxes
* The "Suffix", "Created", and "Modified" fields cannot be edited

Fill out the fields of the form, for example:

| Field       | Value    |
| ----------- | -------- |
| Prefix      | `1903.1` |
| Url         | `https://example.com/test-plan` |
| Repo        | `avalon` |
| Repo Id     | `avalon:test-plan` |
| Description | `Test handle` |
| Notes       | `Handle test for Test Plan` |

and then left-click the "Save" button. The "Select handle to change" page will
be displayed with a notification that the handle was successfully added. Verify
in the handle table that the handle entry was added, and has a "Suffix" that is
one greater than the previous largest suffix entry.

10.3) In the search box, enter `Handle test for Test Plan` and left-click the
"Search" button. Verify that the handle added in the previous step is displayed
in the search results.

### 11\) MD Handle Website - Deleting a handle

11.1) In the search results, left-click the handle that was added in the
previous step. The "Change handle" page will be displayed.

11.2) On the "Change handle" page, left-click the "Delete" button at the
bottom of the page. A "Delete" confirmation page will be displayed.

11.3) On the "Delete" confirmation page, left-click the "Yes, I'm sure" button.
A notification will be displayed indicating that the handle was delete, and
the "Select handle to change" page will be displayed (likely with no entries,
because the search parameter is still being used).

11.4) Left-click the "Handles" entry in the left sidebar. The
"Select handle to change" page will be displayed with a list of handles. Verify
that the deleted handle is no longer in the list.

## Optional Tests

The following tests verify the integration of the "umd-handle-django"
application as a REST service for other applications.

As these steps require creating new items on the applications, it should
***not*** be used to test the production system.

The following steps assume that the user has "administrator" permissions to
the applications.

**Note:** This tests cannot typically be tested in the local development
environment.

### Avalon Integration Test

1\) In a web browser, go to:

* sandbox - <https://av.sandbox.lib.umd.edu/>
* test - <https://av-test.lib.umd.edu/>
* qa - <https://av-qa.lib.umd.edu/>

The Avalon home page will be displayed. Sign in to Avalon using the "Sign in"
button.

2\) Add an item to Avalon, and publish it. On the item page, expand the "Share"
button and verify that the item has an "Item" URL that points to the handle
server associated with the Kubernetes namespace (i.e.,
`https://hdl-<ENV>.lib.umd.edu/<PREFIX>/<SUFFIX>`)

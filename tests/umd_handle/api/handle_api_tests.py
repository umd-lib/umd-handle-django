import json
import pytest
from django.urls import reverse
from umd_handle.api.models import Handle
from umd_handle.api.tokens import create_jwt_token


@pytest.fixture
def override_jwt_secret_setting(settings):
    """
    Overrides the JWT_SECRET setting with a value specific to the tests.
    """
    original_jwt_secret = settings.JWT_SECRET
    settings.JWT_SECRET = 'test_token_secret'

    yield
    settings.JWT_SECRET = original_jwt_secret

@pytest.fixture
def jwt_token(override_jwt_secret_setting) -> str:
    """
    Creates a JWT token using the JWT_SECRET for tests
    """
    return create_jwt_token('pytest test token')

@pytest.fixture
def handle1():
    """
    Creates a handle - 1903.1/1
    """
    return Handle.objects.create(
        prefix='1903.1', suffix = 1, url='http://example.com/',
        repo='fcrepo', repo_id='https://fcrepo-test.lib.umd.edu/fcrepo/test'
    )

@pytest.mark.django_db
def test_handles_exists_requires_jwt_token(client):
    repo = 'fcrepo'
    repo_id = 'https://fcrepo-test.lib.umd.edu/fcrepo/test'
    response = client.get(reverse("handles_exists"), data={'repo': repo, 'repo_id': repo_id})
    assert response.status_code == 401

@pytest.mark.django_db
def test_handles_exists_requires_repo_and_repo_id(client, jwt_token):
    headers = { 'Authorization': f"Bearer {jwt_token}" }

    # "repo" is empty
    response = client.get(reverse("handles_exists"),
                          data={'repo': '', 'repo_id': 'test-repo-id'},
                          headers=headers
                         )
    assert response.status_code == 400

    # "repo_id" missing
    response = client.get(reverse("handles_exists"),
                          data={'repo': 'test-repo'},
                          headers=headers
                         )
    assert response.status_code == 400


@pytest.mark.django_db
def test_handles_exists_return_false_if_handle_does_not_exists(client, jwt_token):
    repo = 'fcrepo'
    repo_id = 'repo-id-does-not-exist'
    headers = { 'Authorization': f"Bearer {jwt_token}" }

    response = client.get(reverse("handles_exists"),
                          data={'repo': repo, 'repo_id': repo_id},
                          headers=headers
                         )

    assert response.status_code == 200
    expected_response = '{"exists": false, "request": {"repo": "fcrepo", "repo_id": "repo-id-does-not-exist"}}'
    assert response.content.decode('utf-8') == expected_response


@pytest.mark.django_db
def test_handles_exists_return_true_if_handle_exists(client, jwt_token, handle1):
    repo = handle1.repo
    repo_id = handle1.repo_id
    headers = { 'Authorization': f"Bearer {jwt_token}" }

    response = client.get(reverse("handles_exists"),
                          data={'repo': repo, 'repo_id': repo_id},
                          headers=headers
                         )

    assert response.status_code == 200
    expected_response = '{"exists": true, "handle_url": "http://hdl-local.lib.umd.edu/1903.1/1", "prefix": "1903.1", "suffix": "1", "url": "http://example.com/", "request": {"repo": "fcrepo", "repo_id": "https://fcrepo-test.lib.umd.edu/fcrepo/test"}}'
    assert response.content.decode('utf-8') == expected_response


@pytest.mark.django_db
def test_handles_info_requires_jwt_token(client):
    repo = '1903.1'
    repo_id = '1'
    response = client.get(reverse("handles_info"), data={'prefix': repo, 'suffix': repo_id})
    assert response.status_code == 401

@pytest.mark.django_db
def test_handles_info_requires_prefix_and_suffix(client, jwt_token):
    headers = { 'Authorization': f"Bearer {jwt_token}" }

    # "prefix" is empty
    response = client.get(reverse("handles_info"),
                          data={'prefix': '', 'suffix': '1'},
                          headers=headers
                         )
    assert response.status_code == 400

    # "suffix" missing
    response = client.get(reverse("handles_info"),
                          data={'prefix': '1903.1'},
                          headers=headers
                         )
    assert response.status_code == 400


@pytest.mark.django_db
def test_handles_info_returns_false_if_handle_does_not_exists(client, jwt_token):
    prefix = 'prefix-does-not-exist'
    suffix = '1'
    headers = { 'Authorization': f"Bearer {jwt_token}" }

    response = client.get(reverse("handles_info"),
                          data={'prefix': prefix, 'suffix': suffix},
                          headers=headers
                         )

    assert response.status_code == 200
    expected_response = '{"exists": false, "request": {"prefix": "prefix-does-not-exist", "suffix": "1"}}'
    assert response.content.decode('utf-8') == expected_response


@pytest.mark.django_db
def test_handles_info_returns_true_if_handle_exists(client, jwt_token, handle1):
    prefix = handle1.prefix
    suffix = handle1.suffix
    headers = { 'Authorization': f"Bearer {jwt_token}" }

    response = client.get(reverse("handles_info"),
                          data={'prefix': prefix, 'suffix': suffix},
                          headers=headers
                         )

    assert response.status_code == 200
    expected_response = '{"exists": true, "handle_url": "http://hdl-local.lib.umd.edu/1903.1/1", "prefix": "1903.1", "suffix": "1", "url": "http://example.com/", "request": {"prefix": "1903.1", "suffix": "1"}}'
    assert response.content.decode('utf-8') == expected_response


@pytest.mark.django_db
def test_handles_prefix_suffix_get_requires_jwt_token(client):
    prefix = '1903.1'
    suffix = '1'
    response = client.get(reverse("handles_prefix_suffix", kwargs={'prefix': prefix, 'suffix': suffix}))
    assert response.status_code == 401

@pytest.mark.django_db
def test_handles_prefix_suffix_get_returns_known_handle(client, jwt_token, handle1):
    prefix = handle1.prefix
    suffix = handle1.suffix
    headers = { 'Authorization': f"Bearer {jwt_token}" }
    response = client.get(reverse("handles_prefix_suffix", kwargs={'prefix': prefix, 'suffix': suffix}),
                           headers=headers)
    assert response.status_code == 200

@pytest.mark.django_db
def test_handles_prefix_suffix_get_returns_404_for_unknown_handle(client, jwt_token):
    prefix = 'UNKNOWN_PREFIX'
    suffix = 1
    headers = { 'Authorization': f"Bearer {jwt_token}" }
    response = client.get(reverse("handles_prefix_suffix", kwargs={'prefix': prefix, 'suffix': suffix}),
                           headers=headers)
    assert response.status_code == 404


@pytest.mark.django_db
def test_handles_mint_new_handle_success(settings, client, jwt_token):
    url = reverse('handles_mint_new_handle')
    headers = {'Authorization': f"Bearer {jwt_token}"}
    body = {
        'prefix': '1903.1',
        'url': 'http://example.com/test',
        'repo': 'fedora2',
        'repo_id': 'test-123'
    }
    response = client.post(
        url, data=json.dumps(body), content_type='application/json', headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data['suffix'] == '1'
    assert data['handle_url'] == f'{settings.HANDLE_HTTP_PROXY_BASE}1903.1/1'
    assert data['request'] == {"prefix":"1903.1","repo":"fedora2","repo_id":"test-123","url":"http://example.com/test"}
    # ensure handle exists in db
    assert Handle.objects.filter(prefix='1903.1', repo_id='test-123').exists()


@pytest.mark.django_db
def test_handles_mint_new_handle_requires_jwt_token(client):
    url = reverse('handles_mint_new_handle')
    body = {
        'prefix': '1903.1',
        'url': 'http://example.com/test',
        'repo': 'fedora2',
        'repo_id': 'test-123'
    }
    response = client.post(
        url, data=json.dumps(body), content_type='application/json'
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_handles_mint_new_handle_validation_errors(client, jwt_token):
    url = reverse('handles_mint_new_handle')
    headers = {'Authorization': f"Bearer {jwt_token}"}

    # missing required parameter 'repo'
    body_missing = {
        'prefix': '1903.1',
        'url': 'http://example.com/test',
        'repo_id': 'test-123'
    }
    resp = client.post(
        url, data=json.dumps(body_missing), content_type='application/json', headers=headers
    )
    assert resp.status_code == 400
    assert "'repo' parameter is required" in resp.json().get('errors', [])

    # invalid prefix should produce validation error
    body_invalid = {
        'prefix': 'BAD_PREFIX',
        'url': 'http://example.com/test',
        'repo': 'fedora2',
        'repo_id': 'test-456'
    }
    resp2 = client.post(
        url, data=json.dumps(body_invalid), content_type='application/json', headers=headers
    )
    assert resp2.status_code == 400
    errors = resp2.json().get('errors', [])
    # message comes from validate_prefix which wraps the value in quotes
    assert any("BAD_PREFIX" in e for e in errors)


@pytest.mark.django_db
def test_handles_prefix_suffix_patch_requires_jwt_token(client, handle1):
    prefix = handle1.prefix
    suffix = handle1.suffix
    body = {'url': 'http://example.com/updated'}
    response = client.patch(
        reverse('handles_prefix_suffix', kwargs={'prefix': prefix, 'suffix': suffix}),
        data=json.dumps(body), content_type='application/json'
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_handles_prefix_suffix_patch_updates_fields(client, jwt_token, handle1):
    prefix = handle1.prefix
    suffix = handle1.suffix
    headers = {'Authorization': f"Bearer {jwt_token}"}
    body = {
        'repo': 'avalon',
        'repo_id': 'new-repo-id',
        'url': 'https://example.org/updated',
        'description': 'Updated description',
        'notes': 'Some notes'
    }
    response = client.patch(
        reverse('handles_prefix_suffix', kwargs={'prefix': prefix, 'suffix': suffix}),
        data=json.dumps(body), content_type='application/json', headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert 'handle_url' in data
    assert data.get('request', {}).get('prefix') == prefix
    assert data.get('request', {}).get('repo') == 'avalon'
    assert data.get('request', {}).get('repo_id') == 'new-repo-id'
    assert data.get('request', {}).get('url') == 'https://example.org/updated'

    # ensure db record updated
    handle = Handle.objects.get(prefix=prefix, suffix=suffix)
    assert handle.repo == 'avalon'
    assert handle.repo_id == 'new-repo-id'
    assert handle.url == 'https://example.org/updated'
    assert handle.description == 'Updated description'
    assert handle.notes == 'Some notes'


@pytest.mark.django_db
def test_handles_prefix_suffix_patch_validation_errors(client, jwt_token, handle1):
    prefix = handle1.prefix
    suffix = handle1.suffix
    headers = {'Authorization': f"Bearer {jwt_token}"}

    # invalid repo value should raise validation error mentioning the bad value
    body = {'repo': 'INVALID_REPO'}
    response = client.patch(
        reverse('handles_prefix_suffix', kwargs={'prefix': prefix, 'suffix': suffix}),
        data=json.dumps(body), content_type='application/json', headers=headers
    )
    assert response.status_code == 400
    errors = response.json().get('errors', [])
    assert any('INVALID_REPO' in e for e in errors)


@pytest.mark.django_db
def test_handles_prefix_suffix_patch_returns_404_for_unknown_handle(client, jwt_token):
    prefix = 'UNKNOWN_PREFIX'
    suffix = 1
    headers = { 'Authorization': f"Bearer {jwt_token}" }
    body = {
        'repo_id': 'new-repo-id',
    }
    response = client.patch(
        reverse('handles_prefix_suffix', kwargs={'prefix': prefix, 'suffix': suffix}),
        data=json.dumps(body), content_type='application/json', headers=headers
    )

    assert response.status_code == 404

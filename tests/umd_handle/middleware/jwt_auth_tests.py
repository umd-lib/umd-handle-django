import jwt
import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from umd_handle.middleware import JWTAuthenticationMiddleware

JWT_SECRET = 'jwt_secret_for_tests'

@pytest.fixture(autouse=True)
def jwt_secret_for_tests(settings):
    settings.JWT_SECRET = 'jwt_secret_for_tests'

@pytest.fixture
def rf():
    """Fixture to provide a RequestFactory instance."""
    return RequestFactory()

def get_response_mock(request):
    """A mock get_response function that returns a simple HttpResponse."""
    return HttpResponse("OK")

def test_non_api_requests_are_ignored(rf):
      middleware = JWTAuthenticationMiddleware(get_response_mock)
      request = rf.get('/')
      response = middleware(request)
      assert response.status_code == 200

def test_requests_without_authorization_header_are_rejected(rf):
      middleware = JWTAuthenticationMiddleware(get_response_mock)
      request = rf.get('/api/vi/handles/1903.1/1')
      response = middleware(request)
      assert response.status_code == 401

def test_requests_without_bearer_in_the_authorization_header_are_rejected(rf):
      middleware = JWTAuthenticationMiddleware(get_response_mock)
      headers = { 'Authorization': 'NOT_VALID' }
      request = rf.get('/api/vi/handles/1903.1/1', headers=headers)
      response = middleware(request)
      assert response.status_code == 401

def test_requests_without_valid_jwt_in_the_authorization_header_are_rejected(rf):
      middleware = JWTAuthenticationMiddleware(get_response_mock)
      headers = { 'Authorization': 'Bearer NOT.VALID.JWT' }
      request = rf.get('/api/vi/handles/1903.1/1', headers=headers)
      response = middleware(request)
      assert response.status_code == 401

def test_jwt_tokens_with_empty_payload_are_rejected(rf):
      middleware = JWTAuthenticationMiddleware(get_response_mock)
      payload = {}
      jwt_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
      headers = { 'Authorization': f"Bearer {jwt_token}" }
      request = rf.get('/api/vi/handles/1903.1/1', headers=headers)
      response = middleware(request)
      assert response.status_code == 401

def test_requests_without_expected_jwt_payload_in_the_authorization_header_are_rejected(rf):
      middleware = JWTAuthenticationMiddleware(get_response_mock)
      payload = { 'foo': 'bar' }
      jwt_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
      headers = { 'Authorization': f"Bearer {jwt_token}" }
      request = rf.get('/api/vi/handles/1903.1/1', headers=headers)
      response = middleware(request)
      assert response.status_code == 401

def test_requests_with_expected_jwt_payload_in_the_authorization_header_are_accepted(rf):
      middleware = JWTAuthenticationMiddleware(get_response_mock)
      payload = { 'role': 'rest_api' }
      jwt_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
      headers = { 'Authorization': f"Bearer {jwt_token}" }
      request = rf.get('/api/vi/handles/1903.1/1', headers=headers)
      response = middleware(request)
      assert response.status_code == 200


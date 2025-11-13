import pytest
from django.core.exceptions import ValidationError
from umd_handle.api.models import Handle

@pytest.fixture
def valid_handle():
    return Handle(
        prefix='1903.1',
        suffix=1,
        url='http://example.com/valid-handle',
        repo='avalon',
        repo_id='avalon-test'
    )

@pytest.mark.django_db
def test_prefix_must_be_known_prefix(valid_handle):
    handle = valid_handle
    handle.prefix = 'INVALID_PREFIX'

    with pytest.raises(ValidationError):
        handle.full_clean()

@pytest.mark.django_db
def test_prefix_must_be_known_repo(valid_handle):
    handle = valid_handle
    handle.repo = 'INVALID_REPO'

    with pytest.raises(ValidationError):
        handle.full_clean()

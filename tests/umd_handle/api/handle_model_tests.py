
import pytest
from django.core.exceptions import ValidationError

from umd_handle.api.models import Handle, mint_new_handle


@pytest.mark.django_db
def test_mint_new_handle_creates_suffix_one_when_no_existing():
	handle = mint_new_handle(
		prefix='1903.1', url='http://example.com/', repo='aspace', repo_id='r1'
	)
	assert isinstance(handle, Handle)
	assert handle.prefix == '1903.1'
	assert handle.suffix == 1
	assert Handle.objects.filter(prefix='1903.1', suffix=1).exists()


@pytest.mark.django_db
def test_mint_new_handle_increments_existing_max_suffix():
	# create some existing handles with suffixes 1 and 3
	Handle.objects.create(prefix='1903.1', suffix=1, url='http://example.com/', repo='aspace', repo_id='r1')
	Handle.objects.create(prefix='1903.1', suffix=3, url='http://example.com/', repo='aspace', repo_id='r2')

	handle = mint_new_handle(
		prefix='1903.1', url='http://example.com/', repo='aspace', repo_id='r3'
	)
	# max was 3, so new should be 4
	assert handle.suffix == 4
	assert Handle.objects.filter(prefix='1903.1', suffix=4).exists()


@pytest.mark.django_db
def test_mint_new_handle_validates_prefix_and_repo():
	# invalid prefix
	with pytest.raises(ValidationError):
		mint_new_handle(
			prefix='INVALID_PREFIX', url='http://example.com/', repo='aspace', repo_id='r1'
		)

	# invalid repo
	with pytest.raises(ValidationError):
		mint_new_handle(
			prefix='1903.1', url='http://example.com/', repo='INVALID_REPO', repo_id='r1'
		)

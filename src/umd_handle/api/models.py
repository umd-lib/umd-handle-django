from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Max
from django.db import transaction
from django_extensions.db.models import TimeStampedModel
from urllib.parse import urlparse

def validate_prefix(value):
    if value not in Handle.ALLOWED_PREFIXES:
        raise ValidationError(f"'{value}' is not an allowed prefix.")

def validate_url(value):
    """
    Using a custom URL validator instead of Django's URLValidator, because
    Avalon may send URLs with a colon immediately after the hostname, i.e.:

    https://av.sandbox.lib.umd.edu:/media_objects/vq27zn67m

    and the Django URLValidator rejects those URLs are invalid.
    """
    parsed_url = urlparse(value)

    if parsed_url.scheme not in ['http', 'https']:
        raise ValidationError(f"'{value}' must use 'http' or 'https' scheme.")

    if not parsed_url.netloc:
        raise ValidationError(f"'{value}' is not a valid URL.")



def validate_repo(value):
    if value not in Handle.ALLOWED_REPOS:
        raise ValidationError(f"'{value}' is not an allowed repo.")


def mint_new_handle(prefix, url, repo, repo_id, description='', notes=''):
    """
    Mint a new Handle by incrementing the suffix from the largest existing
    suffix associated with the prefix.

    Returns the new Handle instance.
    """
    # Use atomic transaction to avoid race condition in generating the
    # next suffix
    with transaction.atomic():
        handle = Handle(
            prefix=prefix,
            suffix=next_suffix(prefix),
            url=url,
            repo=repo,
            repo_id=repo_id,
            description=description,
            notes=notes,
        )

        # Validate and save the handle
        handle.full_clean()
        handle.save()
        return handle


def next_suffix(prefix):
    """
    Calculate the next suffix for the given prefix
    """
    max_suffix = Handle.objects.filter(prefix=prefix) \
        .aggregate(max_suffix=Max('suffix'))['max_suffix']
    next_suffix = (max_suffix or 0) + 1

    return next_suffix

class Handle(TimeStampedModel):

    ALLOWED_PREFIXES = [
        '1903.1',
    ]

    ALLOWED_REPOS = [
        'aspace',
        'avalon',
        'fcrepo',
        'fedora2',
    ]

    prefix = models.CharField(
        choices=[(prefix, prefix) for prefix in ALLOWED_PREFIXES],
        validators=[validate_prefix]
    )
    suffix = models.IntegerField()
    url = models.CharField(validators=[validate_url])
    repo = models.CharField(
        choices=[(repo, repo) for repo in ALLOWED_REPOS],
        validators=[validate_repo]
    )
    repo_id = models.CharField()
    description = models.CharField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['prefix', 'suffix'],
                name='unique_handle_prefix_suffix'
            )
        ]

      # Returns the fully-qualified URL to use as the handle URL
    def handle_url(self):
        return f"{settings.HANDLE_HTTP_PROXY_BASE}{self.prefix}/{self.suffix}"

    def save(self, *args, **kwargs):
        # Use atomic transaction to avoid race condition in generating the
        # next suffix
        with transaction.atomic():
            # When suffix is not set, this must be a new handle, so create and
            # assign the next suffix for the prefix.
            if not self.suffix:
                self.suffix = next_suffix(self.prefix)

            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prefix}/{self.suffix}"


class JWTToken(TimeStampedModel):
    token = models.CharField()
    description = models.CharField()

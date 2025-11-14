from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django_extensions.db.models import TimeStampedModel

def validate_prefix(value):
    if value not in Handle.ALLOWED_PREFIXES:
        raise ValidationError(f"'{value}' is not an allowed prefix.")

def validate_repo(value):
    if value not in Handle.ALLOWED_REPOS:
        raise ValidationError(f"'{value}' is not an allowed repo.")

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
    url = models.CharField(validators=[URLValidator(schemes=['http', 'https'])])
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

class JWTToken(TimeStampedModel):
    token = models.CharField()
    description = models.CharField()

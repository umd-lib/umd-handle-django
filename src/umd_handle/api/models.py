from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.db.models import Max
from django.db import transaction
from django_extensions.db.models import TimeStampedModel

def validate_prefix(value):
    if value not in Handle.ALLOWED_PREFIXES:
        raise ValidationError(f"'{value}' is not an allowed prefix.")


def validate_repo(value):
    if value not in Handle.ALLOWED_REPOS:
        raise ValidationError(f"'{value}' is not an allowed repo.")


def mint_new_handle(prefix, url, repo, repo_id, description='', notes=''):
    """
    Mint a new Handle by incrementing the suffix from the largest existing
    suffix associated with the prefix.

    Returns the new Handle instance.
    """
    # Use atomic transaction to ensure consistency even if there are
    # multiple simultaneous requests.
    with transaction.atomic():
        max_suffix = Handle.objects.filter(prefix=prefix) \
            .aggregate(max_suffix=Max('suffix'))['max_suffix']
        next_suffix = (max_suffix or 0) + 1
        handle = Handle(
            prefix=prefix,
            suffix=next_suffix,
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

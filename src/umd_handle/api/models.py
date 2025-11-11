from django.db import models
from django_extensions.db.models import TimeStampedModel

class Handle(TimeStampedModel):
    prefix = models.CharField()
    suffix = models.IntegerField()
    url = models.CharField()
    repo = models.CharField()
    repo_id = models.CharField()
    description = models.CharField(blank=True)
    notes = models.TextField(blank=True)

class JWTToken(TimeStampedModel):
    token = models.CharField()
    description = models.CharField()

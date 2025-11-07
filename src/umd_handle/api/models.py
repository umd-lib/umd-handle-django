from django.db import models

class Handle(models.Model):
    prefix = models.CharField()
    suffix = models.IntegerField()
    url = models.CharField()
    repo = models.CharField()
    repo_id = models.CharField()
    description = models.CharField(blank=True)
    notes = models.TextField(blank=True)

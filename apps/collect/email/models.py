from datetime import datetime
from django.db import models

class IncidentEmail(models.Model):
    datetime = models.DateTimeField(blank=True, null=True)
    payload = models.CharField(max_length=10000, blank=True, null=True)

    class Meta:
      unique_together = ["payload", "datetime"]
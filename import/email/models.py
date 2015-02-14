from datetime import datetime
import pdb
import re

from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm
from dispatch.models import IncidentManager


class IncidentEmail(models.Model):
    datetime = models.DateTimeField(blank=True, null=True)
    payload = models.CharField(max_length=10000, blank=True, null=True)

    class Meta:
      unique_together = ["payload", "datetime"]
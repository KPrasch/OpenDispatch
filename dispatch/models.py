from datetime import datetime
import re

from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm
from gi.overrides.GLib import Source

    
class Incident(models.Model):
    owner = models.ForeignKey(User)
    source = models.CharField(max_length=200, blank=True)
    payload = models.CharField(max_length=10000, blank=True, null=True)
    lng = models.DecimalField(max_digits=50, decimal_places=1, null= True, blank=True)
    lat = models.DecimalField(max_digits=50, decimal_places=1, null= True, blank=True)
    #zipcode= modelsIntegerField()
    dispatch_time = models.DateTimeField(blank=True, null=True)
    recieved_time = models.DateTimeField(blank=True, null=True)
    created_time = models.DateTimeField(auto_add_now=True)
    #weather_status = IntegerField()

    class Meta:
      unique_together = ["payload", "datetime"]
      order_by = ["datetime"]
      
class IncidentData(models.Model):
    incident = models.ForeignKey(Incident)
    key = models.CharField(max_length=200, blank=True)
    value = models.CharField(max_length=200, blank=True)
    
    


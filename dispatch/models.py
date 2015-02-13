from datetime import datetime
import re

from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm



class GrossHourlyIncidents(models.Model):
    hour = models.IntegerField()
    count = models.IntegerField()

class IncidentManager(models.Manager):
    def create_incident(self):
        incident = self.create()
        # do something with the incident.
        return Incident
    
class RawIncident(models.Model):
    datetime = models.DateTimeField(blank=True, null=True)
    payload = models.CharField(max_length=10000, blank=True, null=True)

    class Meta:
      unique_together = ["payload", "datetime"]
      order_by = ["datetime"]
    
    
#The Unique Dispatch format for Ulster County, NY      
class UlsterIncident(models.Model):
    #source = models.ForeignKey(IncidentEmail, blank=True)
    #call_number = models.IntegerField()
    Unit = models.CharField(max_length=200, blank=True)
    Venue = models.CharField(max_length=500, blank=True)
    #mutual_aid = models.BooleanField(default=False)
    Inc = models.CharField(max_length=600, blank=True)
    Loc = models.CharField(max_length=200, blank=True)
    lat = models.DecimalField(max_digits=50, decimal_places=1, null= True, blank=True)
    long = models.DecimalField(max_digits=50, decimal_places=1, null= True, blank=True)
    XSts = models.CharField(max_length=500, blank=True)
    #dispatch_time = models.DateTimeField('Date and Time of Initial Dispatch')
    Nature = models.CharField(max_length=400, blank=True)
    Common = models.CharField(max_length=200, blank=True)
    Addtl = models.CharField(max_length=200, blank=True)
    Date = models.CharField(max_length=400, blank=True)
    Time = models.CharField(max_length=100, blank=True)
    datetime = models.DateTimeField(blank=True, null=True)
    objects = IncidentManager()

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
    owner = models.ForeignKey(User)
    source = models.ForeignKey(RawIncident)
    Unit = models.CharField(max_length=200, blank=True)
    Venue = models.CharField(max_length=500, blank=True)
    Inc = models.CharField(max_length=600, blank=True)
    Loc = models.CharField(max_length=200, blank=True)
    lat = models.DecimalField(max_digits=50, decimal_places=1, null= True, blank=True)
    long = models.DecimalField(max_digits=50, decimal_places=1, null= True, blank=True)
    XSts = models.CharField(max_length=500, blank=True)
    Nature = models.CharField(max_length=400, blank=True)
    Common = models.CharField(max_length=200, blank=True)
    Addtl = models.CharField(max_length=200, blank=True)
    #zipcode= modelsIntegerField()
    dispatch_time = models.DateTimeField(blank=True, null=True)
    recieved_time = models.DateTimeField(blank=True, null=True)
    created_time = models.DateTimeField(auto_add_now=True)
    #weather_status = IntegerField()
    objects = IncidentManager()
    
    class Meta:
	  order_by = ["dispatch_time"]
    


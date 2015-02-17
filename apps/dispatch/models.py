from datetime import datetime
import re

from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm


class Agency(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField()
    
class Incident(models.Model):
    owner = models.ForeignKey(User)
    payload = models.CharField(max_length=10000, blank=True, null=True)
    lng = models.FloatField()
    lat = models.FloatField()
    zipcode= modelsIntegerField()
    is_active = models.BoleanField(default=False)
    annual_call_number = models.IntegerField()
    dispatch_time = models.DateTimeField(blank=True, null=True)
    recieved_time = models.DateTimeField(blank=True, null=True)
    created_time = models.DateTimeField(auto_add_now=True)
    #weather_status = IntegerField()
    
    class Meta:
      unique_together = ["payload", "datetime"]
      ordering = ["datetime"]
    
    def raw(self):
        return self.payload
    
    def geoloc(self):
        geo_loc = " ".join(self.lat, self.lng)
        return geo_loc
   
    def recieved_delay(self):
        if self.dispatch_time != self.recieved_time:
           delay = (self.dispatch_time-self.recieved_time).total_seconds()
           return delay
        else:
           return None
       
    def created_delay(self):
         if self.recieved_time != self.created_time:
           delay = (self.recieved_time-selfself.created_time).total_seconds()
           return delay
         else:
           return None
       
    def delay(self):
        rd = self.recieved_delay(self)
        cd = self.created_delay(self)
        if rd or cd is not None:
            print "delay detected %s %s" % rd, cd
            return rd, cd
        else:
            return False
            
class IncidentData(models.Model):
    incident = models.ForeignKey(Incident)
    key = models.CharField(max_length=200, blank=True)
    value = models.CharField(max_length=200, blank=True)
    
    def incident(self):
        return self.incident.id
    
from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
import re
from datetime import datetime
import pdb


#DISPATCH_SOURCES = ((0, 'Email'), (1, 'SMS'), (3, 'API'), (4, 'CAD'))

#class Source(models.Model):
#    source = models.IntegerField(default=0, choices=DISPATCH_SOURCES)

class GrossHourlyIncidents(models.Model):
    hour = models.IntegerField()
    count = models.IntegerField()

class IncidentEmail(models.Model):
    datetime = models.DateTimeField(blank=True, null=True)
    payload = models.CharField(max_length=10000, blank=True, null=True)

    class Meta:
      unique_together = ["payload", "datetime"]
      

class IncidentManager(models.Manager):
    def create_incident(self):
        incident = self.create()
        # do something with the incident.
        return Incident

#The Unique Dispatch
class Incident(models.Model):
    #source = models.ForeignKey(IncidentEmail, blank=True)
    #call_number = models.IntegerField()
    payload = models.CharField(max_length=1000, blank=True)
    Unit = models.CharField(max_length=200, blank=True)
    Venue = models.CharField(max_length=500, blank=True)
    #mutual_aid = models.BooleanField(default=False)
    Inc = models.CharField(max_length=600, blank=True)
    Loc = models.CharField(max_length=200, blank=True)
    XSts = models.CharField(max_length=500, blank=True)
    #dispatch_time = models.DateTimeField('Date and Time of Initial Dispatch')
    Nature = models.CharField(max_length=400, blank=True)
    Common = models.CharField(max_length=200, blank=True)
    Addtl = models.CharField(max_length=200, blank=True)
    Date = models.CharField(max_length=400, blank=True)
    Time = models.CharField(max_length=100, blank=True)
    datetime = models.DateTimeField(blank=True, null=True)
    objects = IncidentManager()







# Under Construction:




'''



    def save(self, *args, **kwargs):
      #pdb.set_trace()
      msg = self.payload
      if self.Venue == '' and bool(re.search("Paltz", msg)) == True:
          self.Venue = "New Paltz"
      else:
        self.Venue
      if self.Loc == '':

      super(Incident, self).save(*args, **kwargs)

class Incident_Form(ModelForm):
           class Meta:
               model = Incident


# Need GeoDjango Integration Here.
class Location(models.Model):
    latitude = models.IntegerField()
    longitude = models.IntegerField()
    country = 'USA'
    state = models.IntegerField()
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    address_number = models.IntegerField()
    interscection = models.CharField(max_length=100)

'''

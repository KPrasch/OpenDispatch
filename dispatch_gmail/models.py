from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User


#DISPATCH_SOURCES = ((0, 'Email'), (1, 'SMS'), (3, 'API'), (4, 'CAD'))

#class Source(models.Model):
#    source = models.IntegerField(default=0, choices=DISPATCH_SOURCES)

class GrossHourlyIncidents(models.Model):
    hour = models.IntegerField()
    count = models.IntegerField()

class IncidentEmail(models.Model):
    datetime_str = models.CharField(max_length=10000, blank=True)
    payload = models.CharField(max_length=10000, blank=True, null=True)
    class Meta:
      unique_together = ["payload", "datetime_str"]

class IncidentManager(models.Manager):
    def create_incident(self):
        incident = self.create()
        # do something with the incident.
        return Incident

#The Unique Dispatch
class Incident(models.Model):
    #source = models.ForeignKey(IncidentEmail, blank=True)
    #call_number = models.IntegerField()
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
    datetime_str = models.DateTimeField()

    objects = IncidentManager()

    class Meta:
      unique_together = ["Inc", "datetime_str"]


# Under Construction:
'''

    def clean(self):
        cleaned_incident_fields = super(Incident, self).clean()
        loc = cleaned_incident_field.get("Loc")
        xsts = cleaned_incident_field.get("Xsts")
        nature = cleaned_incident_field.get("Nature")
        common = cleaned_incident_field.get("Common")
        addtl = cleaned_incident_field.get("Addtl")
        date = cleaned_incident_field.get("Date")
        time  = cleaned_incident_field.get("Time")

        return cleaned_incident_fields


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

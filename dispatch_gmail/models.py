from django.db import models



DISPATCH_SOURCES = ((0, 'Email'), (1, 'SMS'), (3, 'API'), (4, 'CAD'))


#pseudocode for accepting future input sources
class Source(models.Model):
    source = models.IntegerField(default=0, choices=DISPATCH_SOURCES)

class Email(models.Model):
    sender = models.EmailField(max_length=256)
    subject = models.CharField(max_length=100)
    body = models.TextField()

class IncidentManager(models.Manager):
    def create_incident(self, unit):
        incident = self.create(unit='43')
        # do something with the incident.
        return Incident

#The Unique Dispatch
class Incident(models.Model):
    #Hardcoded to email sources for now.
    source = models.ForeignKey(Source)
    call_number = models.IntegerField()
    unit = models.CharField(max_length=20)
    venue = models.CharField(max_length=50)
    mutual_aid = models.BooleanField(default=False)
    incident = models.CharField(max_length=600)
    location = models.CharField(max_length=200)
    interscection = models.CharField(max_length=50)
    dispatch_time = models.DateTimeField('Date and Time of Initial Dispatch')
    nature = models.CharField(max_length=100)
    common = models.CharField(max_length=200)
    additional = models.CharField(max_length=200)

    objects = IncidentManager()

'''
#Need GeoDjango Integration Here.
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

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
    def create_incident(self):
        incident = self.create()
        # do something with the incident.
        return Incident

#keys = set(('Inc', 'Nature', 'XSts', 'Common', 'Addtl', 'Loc', 'Date', 'Unit'))

#The Unique Dispatch
class Incident(models.Model):
    #Hardcoded to email sources for now.
    source = models.ForeignKey(Source)
    call_number = models.IntegerField()
    Unit = models.CharField(max_length=20)
    venue = models.CharField(max_length=50)
    mutual_aid = models.BooleanField(default=False)
    Inc = models.CharField(max_length=600)
    Loc = models.CharField(max_length=200)
    XSts = models.CharField(max_length=50)
    dispatch_time = models.DateTimeField('Date and Time of Initial Dispatch')
    Nature = models.CharField(max_length=100)
    Common = models.CharField(max_length=200)
    Addtl = models.CharField(max_length=200)
    Date = models.CharField(max_length=100)

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

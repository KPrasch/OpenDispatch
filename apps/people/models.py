from django.contrib.auth.models import User
from django.contrib.gis.measure import D
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.db import models
from phonenumber_field.modelfields import PhoneNumberField

ROLES = (
    ('Medical Responder', 'Medical Responder'),
    ('Firefighter', 'Firefighter'),
    ('Administrator', 'Administrator'),
    ('Radio Hobbiest', 'Radio Hobbiest'),
    ('Law Enforcement', 'Law Enforcement'),
    ('Public Works', 'Public Works'),
    ('Other Government Employee', 'Other Government Employee'),
    ('Technical', 'Technical')
)


class Account(models.Model):
    user = models.OneToOneField(User)
    phone_number = PhoneNumberField(blank=True, default=None)
    agency = models.CharField(max_length=64, blank=True, null=True)
    role = models.CharField(choices=ROLES, max_length=256, blank=True, null=True)
    # firehose = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

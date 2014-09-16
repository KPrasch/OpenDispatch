from django.db import models

# Create your models here.

class Dispatch(models.Model):
    unit =
    venue =
    incident = models.CharField(max_length=600)
    location =
    interscection =
    dispatch_time = models.DateTimeField('Date and Time of Initial Dispatch')
    nature =
    common =
    additional =

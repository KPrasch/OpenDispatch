from django.db import models

# Create your models here.

class Email(models.Model):
    sender = models.EmailField(max_length=256)
    subject = models.CharField(max_length=100)
    body = models.TextField()


class Dispatch(models.Model):
    source = models.ForeignKey(email)
    unit = models.CharField(max_length=20)
    venue = models.CharField(max_length=50)
    incident = models.CharField(max_length=600)
    location = models.CharField(max_length=200)
    interscection = models.CharField(max_length=50)
    dispatch_time = models.DateTimeField('Date and Time of Initial Dispatch')
    nature = models.CharField(max_length=100)
    common = models.CharField(max_length=200)
    additional = models.CharField(max_length=200)

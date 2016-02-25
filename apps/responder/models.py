from django.contrib.auth.models import User
from apps.people.models import Account
from django.db import models
import datetime

class ResponderCall(models.Model):
    account = models.ForeignKey(Account)
    call_time = models.DateTimeField(default= datetime.datetime.now())


from django.db import models
from django.contrib.auth.models import User
    
    
class UserProfile(models.Model):
    owner = models.OneToOneField(User)

    def __str__(self):  
         return "%s's profile" % self.user
    
class Agency(models.Model):
    owner = models.ForeignKey(UserProfile)
    
class Dispatch(models.Model):
    owner = models.ForeignKey(UserProfile)
    #fields = config.dispatch_settings.KEYS
    
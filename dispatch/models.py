
    
    
class UserProfile(models.Model):
    owner = models.OnetoOneField(User)
    agency = models.ForeignKey(Agency)
    def __str__(self):  
         return "%s's profile" % self.user
    
class Agency(models.Model):
    owner = models.ForeignKey(UserProfile)
    
class Dispatch(models.Model):
    keys
from django.db import models
from accounts.models import User,UserProfile
# Create your models here.


class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user',on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile',on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_license=models.ImageField(upload_to = 'vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    vendor_slug = models.SlugField(max_length=100,unique=True)


    def __str__(self):
        return self.vendor_name
    
DAYS = [
    (1,('Monday')),
    (2,('Tuesday')),
    (3,('Wednesday')),
    (4,('Thursday')),
    (5,('Friday')),
    (6,('Saturday')),
    (7,('Sunday')),
]

HOURS_OF_DAY_24 = [
    
]

class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField()
    to_hour = models.CharField()
    is_closed = models.BooleanField(default=False)

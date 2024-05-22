from django.db import models
from django.db.models.fields.related import ForeignKey, OneToOneField

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point

# Create your models here.
# We are extending out user models for some more advanced management of them (eg Customer or Vendor groups)

# Extends the original BaseUserManager class
class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')
        
        if not username:
            raise ValueError('User must have a username entered')
        
        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user


# Extends the original BaseUserManager class
# want to tell Django to use the email field as the user login, also add extra fields to the user like rolls (customer, vendor)
class User(AbstractBaseUser):

    RESTAURANT = 1
    CUSTOMER = 2

    ROLE_CHOICE = (
        (RESTAURANT,'Restaurant'),
        (CUSTOMER,'Customer')
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=12, blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICE, blank=True, null=True)

    # required fields

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    # authentication part

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name','last_name']

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, add_label):
        return True

    def get_role(self):
        if self.role == 1:
            #customer
            user_role = 'Vendor'

        elif self.role == 2:
            user_role = 'Customer'

        return user_role

class UserProfile(models.Model):
    user = OneToOneField(User, on_delete = models.CASCADE, blank =True, null=True)
    profile_picture = models.ImageField(upload_to='users/profile_pictures',blank=True,null=True)
    cover_photo =  models.ImageField(upload_to='users/cover_photos',blank=True,null=True)
    address = models.CharField(max_length=250,blank=True,null=True)
    country = models.CharField(max_length=25,blank=True,null=True)
    state = models.CharField(max_length=25,blank=True,null=True)
    pin_code = models.CharField(max_length=6,blank=True,null=True)
    latitude = models.CharField(max_length=20, blank =True, null=True)
    longitude = models.CharField(max_length=20, blank =True, null=True)
    location = gismodels.PointField(blank=True, null=True,srid=4326)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    

    def save(self,*args,**kwargs):
        if self.latitude and self.longitude:
            self.location = Point(float(self.longitude),float(self.latitude))
            return super(UserProfile,self).save(*args,**kwargs)
        return super(UserProfile,self).save(*args,**kwargs)


    def __str__(self):
        return self.user.email
    




#### one way to connect the sender and reciever
# post_save.connect(post_save_create_profile_reciever,sender=User)


#### better way = use decorator


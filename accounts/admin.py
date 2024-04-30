from django.contrib import admin
from .models import User, UserProfile
from django.contrib.auth.admin import UserAdmin

# Register your models here.
# we have changed the User model (base out of the box definition, so need to bring the new definition in here so the admin panel can see it)

class CustomUserAdmin(UserAdmin):
    list_display = (
        'email','first_name','last_name','username','phone_number','role','is_active'
    )
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()



admin.site.register(User,CustomUserAdmin)
admin.site.register(UserProfile)

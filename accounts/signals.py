from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import User, UserProfile

@receiver(post_save, sender=User)
def post_save_create_profile_reciever(sender, instance, created,**kwargs):
    print(created)
    if created:
        UserProfile.objects.create(user=instance)
        #print('user profile is created')

    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # new profile needs to be created if it does not exist
            UserProfile.objects.create(user=instance)
            #print('profile did not exist, user profile is created')

        #print('user is updated')


# will trigger before the user is created
@receiver(pre_save, sender = User)
def pre_save_profile_receiver(sender, instance, **kwags):
    pass
    #print(instance.username, 'this user is being saved')
    

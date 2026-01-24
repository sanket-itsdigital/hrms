from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from accounts.models import User
from company.models import BirthdayAnniversary


@receiver(post_save, sender=User)
def sync_birthday_anniversary(sender, instance, created, **kwargs):
    """
    Automatically sync User's birth_date and date_of_joining to BirthdayAnniversary model
    """
    # Get or create BirthdayAnniversary record
    ba, created_ba = BirthdayAnniversary.objects.get_or_create(user=instance)
    
    # Update fields from User model
    ba.birth_date = instance.birth_date
    ba.joining_date = instance.date_of_joining
    ba.save()


@receiver(post_delete, sender=User)
def delete_birthday_anniversary(sender, instance, **kwargs):
    """
    Delete BirthdayAnniversary when User is deleted
    """
    try:
        BirthdayAnniversary.objects.filter(user=instance).delete()
    except BirthdayAnniversary.DoesNotExist:
        pass

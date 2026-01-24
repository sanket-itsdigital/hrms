"""
Management command to sync User model's birth_date and date_of_joining 
to BirthdayAnniversary model for existing users.
"""
from django.core.management.base import BaseCommand
from accounts.models import User
from company.models import BirthdayAnniversary


class Command(BaseCommand):
    help = 'Sync User model birth_date and date_of_joining to BirthdayAnniversary model'

    def handle(self, *args, **options):
        self.stdout.write('Starting sync of birthdays and anniversaries...')
        
        users = User.objects.filter(is_active=True)
        synced_count = 0
        created_count = 0
        
        for user in users:
            ba, created = BirthdayAnniversary.objects.get_or_create(user=user)
            
            # Update from User model
            if user.birth_date:
                ba.birth_date = user.birth_date
            if user.date_of_joining:
                ba.joining_date = user.date_of_joining
            
            ba.save()
            
            if created:
                created_count += 1
            else:
                synced_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully synced {synced_count} existing records and created {created_count} new records.'
            )
        )

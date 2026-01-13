"""
Management command to create default roles with permissions.
Run: python manage.py setup_roles
"""
from django.core.management.base import BaseCommand
from accounts.models import Role
from accounts.permissions_config import PERMISSIONS


class Command(BaseCommand):
    help = 'Create default roles with permissions'

    def handle(self, *args, **options):
        self.stdout.write('Creating roles with permissions...')
        
        roles_data = [
            {
                'name': 'CEO',
                'display_name': 'CEO',
                'description': 'Chief Executive Officer - Full admin access',
            },
            {
                'name': 'HR',
                'display_name': 'HR',
                'description': 'Human Resources - Manages attendance, leaves, and payroll',
            },
            {
                'name': 'PM',
                'display_name': 'Project Manager',
                'description': 'Project Manager - Manages assigned projects and tasks',
            },
            {
                'name': 'DEV',
                'display_name': 'Developer',
                'description': 'Developer - Works on assigned projects and tasks',
            },
            {
                'name': 'UIUX',
                'display_name': 'UI/UX Designer',
                'description': 'UI/UX Designer - Works on design tasks and assets',
            },
            {
                'name': 'BDE',
                'display_name': 'Business Development Executive',
                'description': 'BDE - Manages leads and business development',
            },
        ]
        
        for role_data in roles_data:
            role_name = role_data['name']
            permissions = PERMISSIONS.get(role_name, {})
            
            role, created = Role.objects.update_or_create(
                name=role_name,
                defaults={
                    'display_name': role_data['display_name'],
                    'description': role_data['description'],
                    'permissions': permissions,
                    'is_active': True,
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created role: {role.display_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated role: {role.display_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\n✓ All roles created/updated successfully!')
        )

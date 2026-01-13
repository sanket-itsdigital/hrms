"""
Management command to display all role permissions.
Run: python manage.py show_permissions
"""
from django.core.management.base import BaseCommand
from accounts.permissions_config import PERMISSIONS, get_role_permissions


class Command(BaseCommand):
    help = 'Display all role permissions'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== HRMS Role Permissions ===\n'))
        
        for role_name, role_perms in PERMISSIONS.items():
            self.stdout.write(self.style.HTTP_INFO(f'\n{"="*60}'))
            self.stdout.write(self.style.HTTP_INFO(f'ROLE: {role_name}'))
            self.stdout.write(self.style.HTTP_INFO(f'{"="*60}\n'))
            
            for module, actions in role_perms.items():
                self.stdout.write(self.style.WARNING(f'\n  Module: {module.upper()}'))
                self.stdout.write('  ' + '-'*50)
                
                for action, allowed in actions.items():
                    status = '✓' if allowed else '✗'
                    color = self.style.SUCCESS if allowed else self.style.ERROR
                    self.stdout.write(f'    {status} {action:20} : {color(str(allowed))}')
        
        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}\n'))

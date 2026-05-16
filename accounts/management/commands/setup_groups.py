"""
Management command: python manage.py setup_groups
Creates the 4 BraveCare role-based Django Groups with appropriate permissions.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


GROUPS = {
    'System Administrator': '__all__',
    'Outreach Coordinator': [
        ('patients',   'patient',           ['view']),
        ('outreach',   'outreachcampaign',  ['add', 'change', 'delete', 'view']),
        ('volunteers', 'volunteer',         ['add', 'change', 'delete', 'view']),
        ('patients',   'followup',          ['view']),
        ('patients',   'screening',         ['view']),
        ('communication', 'communicationmessage', ['add', 'change', 'view']),
    ],
    'Healthcare Worker': [
        ('patients',   'patient',           ['add', 'change', 'view']),
        ('patients',   'screening',         ['add', 'change', 'view']),
        ('patients',   'followup',          ['add', 'change', 'view']),
        ('patients',   'maternalchildhealth', ['add', 'change', 'view']),
    ],
    'Volunteer': [
        ('patients',   'patient',           ['view']),
        ('outreach',   'outreachcampaign',  ['view']),
        ('patients',   'followup',          ['view']),
    ],
}


class Command(BaseCommand):
    help = 'Create the 4 BraveCare role-based Django Groups with permissions'

    def handle(self, *args, **options):
        all_permissions = Permission.objects.all()

        for group_name, perms in GROUPS.items():
            group, created = Group.objects.get_or_create(name=group_name)
            group.permissions.clear()

            if perms == '__all__':
                group.permissions.set(all_permissions)
                self.stdout.write(f'  {group_name}: assigned ALL permissions')
            else:
                assigned = []
                for app_label, model_name, actions in perms:
                    try:
                        ct = ContentType.objects.get(app_label=app_label, model=model_name)
                        for action in actions:
                            codename = f'{action}_{model_name}'
                            perm = Permission.objects.filter(content_type=ct, codename=codename).first()
                            if perm:
                                group.permissions.add(perm)
                                assigned.append(codename)
                    except ContentType.DoesNotExist:
                        self.stdout.write(self.style.WARNING(
                            f'  ContentType not found: {app_label}.{model_name}'
                        ))
                self.stdout.write(f'  {group_name}: {len(assigned)} permissions assigned')

            action = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f'{action} group: {group_name}'))

        self.stdout.write(self.style.SUCCESS('\nGroups setup complete.'))

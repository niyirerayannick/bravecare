"""
Management command: python manage.py seed_users

Creates one demo account for each BraveCare role.
Safe to re-run: updates passwords and profiles if users already exist.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

from accounts.models import UserProfile


SEED_USERS = [
    {
        'username':   'admin',
        'password':   'Admin@1234',
        'first_name': 'System',
        'last_name':  'Administrator',
        'email':      'admin@bravecare.org',
        'role':       'system_administrator',
        'is_staff':   True,
        'is_superuser': True,
        'group':      'System Administrator',
    },
    {
        'username':   'coordinator',
        'password':   'Coord@1234',
        'first_name': 'Jane',
        'last_name':  'Coordinator',
        'email':      'coordinator@bravecare.org',
        'role':       'coordinator',
        'is_staff':   False,
        'is_superuser': False,
        'group':      'Outreach Coordinator',
    },
    {
        'username':   'healthworker',
        'password':   'Health@1234',
        'first_name': 'James',
        'last_name':  'Mwangi',
        'email':      'healthworker@bravecare.org',
        'role':       'healthcare_worker',
        'is_staff':   False,
        'is_superuser': False,
        'group':      'Healthcare Worker',
    },
    {
        'username':   'volunteer',
        'password':   'Volunt@1234',
        'first_name': 'Mary',
        'last_name':  'Volunteer',
        'email':      'volunteer@bravecare.org',
        'role':       'volunteer',
        'is_staff':   False,
        'is_superuser': False,
        'group':      'Volunteer',
    },
]


class Command(BaseCommand):
    help = 'Seed one demo user per BraveCare role (safe to re-run)'

    def handle(self, *args, **options):
        self.stdout.write('\nSeeding BraveCare demo users...\n')

        col_w = (12, 20, 14, 16)
        header = (
            f"  {'Username':<{col_w[0]}} {'Full Name':<{col_w[1]}} "
            f"{'Password':<{col_w[2]}} {'Role':<{col_w[3]}}"
        )
        divider = '  ' + '-' * (sum(col_w) + len(col_w) * 1 + 2)

        self.stdout.write(self.style.HTTP_INFO(header))
        self.stdout.write(divider)

        for data in SEED_USERS:
            user, created = User.objects.get_or_create(username=data['username'])
            user.first_name   = data['first_name']
            user.last_name    = data['last_name']
            user.email        = data['email']
            user.is_staff     = data['is_staff']
            user.is_superuser = data['is_superuser']
            user.is_active    = True
            user.set_password(data['password'])
            user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role   = data['role']
            profile.status = 'active'
            profile.save()

            # Assign Django Group
            try:
                group = Group.objects.get(name=data['group'])
                user.groups.set([group])
            except Group.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"  Warning: Group '{data['group']}' not found. Run setup_groups first."
                ))

            tag = 'Created' if created else 'Updated'
            full_name = f"{data['first_name']} {data['last_name']}"
            row = (
                f"  {data['username']:<{col_w[0]}} {full_name:<{col_w[1]}} "
                f"{data['password']:<{col_w[2]}} {data['role']:<{col_w[3]}}"
                f"  [{tag}]"
            )
            self.stdout.write(self.style.SUCCESS(row))

        self.stdout.write(divider)
        self.stdout.write(
            self.style.WARNING(
                '\n  These are development credentials. '
                'Change all passwords before deploying to production.\n'
            )
        )

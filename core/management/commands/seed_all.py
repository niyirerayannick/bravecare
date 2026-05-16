"""
Seed everything in the correct order.
Usage:
  python manage.py seed_all              # locations + admin user only (production)
  python manage.py seed_all --demo       # + demo patients, campaigns, volunteers, messages
  python manage.py seed_all --demo --clear  # wipe app data first, then seed everything
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Seed all reference data (locations) and optionally demo data'

    def add_arguments(self, parser):
        parser.add_argument('--demo', action='store_true', help='Also seed demo patients, campaigns, volunteers, messages')
        parser.add_argument('--clear', action='store_true', help='Clear existing app data before seeding (requires --demo)')

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== BraveCare Seed All ===\n'))

        # 1. Provinces, Districts, Sectors
        self.stdout.write(self.style.MIGRATE_LABEL('Step 1/3: Seeding provinces, districts, sectors...'))
        call_command('seed_rwanda_locations', verbosity=0)
        self.stdout.write(self.style.SUCCESS('  Done.\n'))

        # 2. Cells and Villages
        self.stdout.write(self.style.MIGRATE_LABEL('Step 2/3: Seeding cells and villages (this takes ~30s)...'))
        call_command('seed_rwanda_cells', verbosity=0)
        self.stdout.write(self.style.SUCCESS('  Done.\n'))

        # 3. Superuser
        self.stdout.write(self.style.MIGRATE_LABEL('Step 3/3: Ensuring admin user exists...'))
        self._ensure_admin()
        self.stdout.write(self.style.SUCCESS('  Done.\n'))

        # 4. Demo data (optional)
        if options['demo']:
            self.stdout.write(self.style.MIGRATE_LABEL('Step 4/4: Seeding demo data...'))
            if options['clear']:
                call_command('seed_data', clear=True, verbosity=1)
            else:
                call_command('seed_data', verbosity=1)
            self.stdout.write(self.style.SUCCESS('  Done.\n'))

        self.stdout.write(self.style.SUCCESS('=== Seed complete! ===\n'))

    def _ensure_admin(self):
        if not User.objects.filter(username='admin').exists():
            user = User.objects.create_superuser(
                username='admin',
                email='admin@bravecare.org',
                password='BraveCare@2025!',
            )
            UserProfile.objects.get_or_create(user=user, defaults={'role': 'admin'})
            self.stdout.write(self.style.WARNING(
                '  Created admin user. Login: admin / BraveCare@2025!\n'
                '  IMPORTANT: Change this password immediately after first login.'
            ))
        else:
            self.stdout.write('  Admin user already exists.')

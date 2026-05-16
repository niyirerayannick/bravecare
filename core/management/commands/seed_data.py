"""
Management command to populate the database with realistic demo data.
Usage: python manage.py seed_data
"""
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from patients.models import Patient, Screening, MaternalChildHealth, FollowUp
from outreach.models import OutreachCampaign
from volunteers.models import Volunteer
from communication.models import CommunicationMessage


LOCATIONS = [
    "Kibera, Nairobi", "Mathare, Nairobi", "Korogocho, Nairobi",
    "Huruma, Nairobi", "Kangemi, Nairobi", "Kawangware, Nairobi",
    "Mukuru, Nairobi", "Eastleigh, Nairobi", "Ruiru, Kiambu",
    "Thika, Kiambu", "Limuru, Kiambu", "Kikuyu, Kiambu",
    "Nakuru Central", "Nakuru East", "Gilgil, Nakuru",
    "Kisumu Central", "Kisumu East", "Nyalenda, Kisumu",
    "Mombasa Island", "Likoni, Mombasa", "Kisauni, Mombasa",
    "Eldoret Town", "Huruma, Uasin Gishu", "Moi's Bridge",
]

FIRST_NAMES_M = ["James", "John", "David", "Michael", "Peter", "Paul", "Joseph",
                  "Simon", "Thomas", "Daniel", "Samuel", "Moses", "Isaac", "Elijah", "Caleb"]
FIRST_NAMES_F = ["Mary", "Grace", "Faith", "Joyce", "Esther", "Agnes", "Ruth",
                  "Dorothy", "Catherine", "Patricia", "Jane", "Susan", "Rose", "Alice", "Miriam"]
LAST_NAMES = ["Kamau", "Odhiambo", "Mutua", "Mwangi", "Otieno", "Achieng", "Wambui",
               "Njoroge", "Kariuki", "Adhiambo", "Wanjiku", "Ndung'u", "Gitonga",
               "Muthoni", "Wairimu", "Njeri", "Kimani", "Kiprotich", "Chepkorir", "Chebet"]

SCREENING_TYPES = [
    "Blood Pressure", "Malaria RDT", "HIV Rapid Test", "Tuberculosis Screen",
    "Diabetes (Blood Sugar)", "Cervical Cancer (VIA)", "Breast Examination",
    "Eye Examination", "Dental Screening", "Nutrition Assessment",
]

SERVICES = [
    "General Check-up", "Hypertension Follow-up", "Diabetes Management",
    "Antenatal Visit", "Immunization", "TB Treatment", "HIV/ARV Refill",
    "Wound Dressing", "Physiotherapy", "Nutritional Counseling",
    "Mental Health Check", "Family Planning", "Child Growth Monitoring",
]

CAMPAIGN_DATA = [
    {
        "title": "Kibera Community Health Camp 2025",
        "description": "Mass health screening and free consultation camp targeting residents of Kibera slum covering HIV testing, malaria RDT, blood pressure screening, and nutrition assessment.",
        "location": "Kibera Community Centre, Nairobi",
        "status": "active",
    },
    {
        "title": "Maternal Health Awareness Drive – Kisumu",
        "description": "Community education and service delivery campaign focused on antenatal care, skilled birth attendance, and postnatal care in low-income Kisumu settlements.",
        "location": "Nyalenda, Kisumu",
        "status": "active",
    },
    {
        "title": "TB Awareness & Screening Campaign – Mathare",
        "description": "Door-to-door tuberculosis screening and education campaign targeting high-density informal settlement with high TB burden.",
        "location": "Mathare, Nairobi",
        "status": "planned",
    },
    {
        "title": "Childhood Immunization Outreach – Nakuru",
        "description": "Routine immunization catch-up program targeting children under 5 years who missed scheduled vaccinations during COVID-19 disruptions.",
        "location": "Nakuru East Sub-county",
        "status": "completed",
    },
    {
        "title": "Diabetes & Hypertension Screening – Mombasa",
        "description": "Non-communicable disease screening and health education targeting adult populations in coastal communities.",
        "location": "Kisauni, Mombasa",
        "status": "planned",
    },
    {
        "title": "Mental Health Awareness Week – Eldoret",
        "description": "Community-based mental health awareness campaign with free counseling sessions, stigma reduction activities, and referral to care.",
        "location": "Eldoret Town, Uasin Gishu",
        "status": "active",
    },
]


class Command(BaseCommand):
    help = 'Seeds the database with realistic demo data for BraveCare Outreach'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data first')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            CommunicationMessage.objects.all().delete()
            FollowUp.objects.all().delete()
            MaternalChildHealth.objects.all().delete()
            Screening.objects.all().delete()
            OutreachCampaign.objects.all().delete()
            Volunteer.objects.all().delete()
            Patient.objects.all().delete()
            UserProfile.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.WARNING('Existing data cleared.'))

        self.stdout.write('Creating users...')
        self._create_users()

        self.stdout.write('Creating patients...')
        self._create_patients()

        self.stdout.write('Creating outreach campaigns...')
        self._create_campaigns()

        self.stdout.write('Creating volunteers...')
        self._create_volunteers()

        self.stdout.write('Creating communication messages...')
        self._create_messages()

        self.stdout.write(self.style.SUCCESS(
            '\nSeed data created successfully!\n'
            '   Admin credentials: admin / admin123\n'
            '   Run: python manage.py runserver\n'
        ))

    def _create_users(self):
        users_data = [
            ('admin', 'Admin', 'User', 'admin@bravecare.org', 'admin123', True, 'admin'),
            ('coordinator1', 'Sarah', 'Kamau', 'sarah@bravecare.org', 'bravecare2025', False, 'coordinator'),
            ('hw_mwangi', 'David', 'Mwangi', 'david@bravecare.org', 'bravecare2025', False, 'healthcare_worker'),
            ('hw_achieng', 'Grace', 'Achieng', 'grace@bravecare.org', 'bravecare2025', False, 'healthcare_worker'),
            ('dm_kipchoge', 'Eric', 'Kipchoge', 'eric@bravecare.org', 'bravecare2025', False, 'data_manager'),
        ]
        for username, first, last, email, pwd, is_super, role in users_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username, first_name=first, last_name=last,
                    email=email, password=pwd, is_superuser=is_super, is_staff=is_super
                )
                UserProfile.objects.get_or_create(user=user, defaults={'role': role})
                self.stdout.write(f'  Created user: {username}')

    def _create_patients(self):
        today = date.today()
        admin_user = User.objects.filter(username='admin').first()

        patients = []
        for i in range(25):
            gender = random.choice(['M', 'F'])
            first_name = random.choice(FIRST_NAMES_M if gender == 'M' else FIRST_NAMES_F)
            last_name = random.choice(LAST_NAMES)
            age_years = random.randint(16, 75)
            dob = today - timedelta(days=age_years * 365 + random.randint(0, 365))
            risk = random.choices(['low', 'medium', 'high'], weights=[50, 30, 20])[0]

            patient, created = Patient.objects.get_or_create(
                national_id=f"KE{random.randint(10000000, 39999999)}",
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': f"+2547{random.randint(10000000, 99999999)}",
                    'date_of_birth': dob,
                    'gender': gender,
                    'location': random.choice(LOCATIONS),
                    'risk_level': risk,
                    'notes': random.choice([
                        '', '', '',
                        'Patient has history of hypertension.',
                        'Requires close monitoring for diabetes.',
                        'On ARV treatment. Adherence good.',
                        'Pregnant, second trimester.',
                        'Elderly with multiple comorbidities.',
                    ])
                }
            )
            if created:
                patients.append(patient)
                self._create_screenings(patient, admin_user)
                self._create_followups(patient, admin_user)
                if patient.gender == 'F' and patient.age < 50:
                    self._create_mch(patient, admin_user)

        self.stdout.write(f'  Created {len(patients)} patients')

    def _create_screenings(self, patient, user):
        num = random.randint(1, 3)
        for _ in range(num):
            screening_date = date.today() - timedelta(days=random.randint(1, 180))
            Screening.objects.create(
                patient=patient,
                screening_type=random.choice(SCREENING_TYPES),
                result=random.choices(
                    ['normal', 'abnormal', 'pending', 'referred'],
                    weights=[50, 20, 20, 10]
                )[0],
                risk_level=patient.risk_level,
                screening_date=screening_date,
                performed_by=user,
            )

    def _create_followups(self, patient, user):
        num = random.randint(1, 4)
        for _ in range(num):
            days_offset = random.randint(-60, 30)
            due_date = date.today() + timedelta(days=days_offset)
            if days_offset < -5:
                status = random.choices(['completed', 'missed'], weights=[70, 30])[0]
            elif days_offset < 0:
                status = random.choices(['completed', 'missed', 'pending'], weights=[40, 30, 30])[0]
            else:
                status = 'pending'

            FollowUp.objects.create(
                patient=patient,
                service=random.choice(SERVICES),
                due_date=due_date,
                status=status,
                assigned_to=user,
            )

    def _create_mch(self, patient, user):
        num = random.randint(1, 3)
        service_types = ['antenatal', 'postnatal', 'immunization', 'nutrition',
                          'family_planning', 'child_growth']
        for _ in range(num):
            visit_date = date.today() - timedelta(days=random.randint(7, 120))
            next_date = visit_date + timedelta(days=random.randint(14, 60))
            MaternalChildHealth.objects.create(
                patient=patient,
                service_type=random.choice(service_types),
                visit_date=visit_date,
                next_followup_date=next_date,
                attended_by=user,
            )

    def _create_campaigns(self):
        admin_user = User.objects.filter(username='admin').first()
        today = date.today()

        for i, data in enumerate(CAMPAIGN_DATA):
            start = today - timedelta(days=random.randint(0, 30))
            end = start + timedelta(days=random.randint(14, 60))
            target = random.randint(200, 1000)
            reached = int(target * random.uniform(0.3, 0.95)) if data['status'] != 'planned' else 0

            OutreachCampaign.objects.get_or_create(
                title=data['title'],
                defaults={
                    'description': data['description'],
                    'location': data['location'],
                    'start_date': start,
                    'end_date': end,
                    'status': data['status'],
                    'target_population': target,
                    'reached_count': reached,
                    'created_by': admin_user,
                }
            )
        self.stdout.write(f'  Created {len(CAMPAIGN_DATA)} campaigns')

    def _create_volunteers(self):
        volunteer_data = [
            ('Jane', 'Wanjiku', '+254712345678', 'jane.wanjiku@email.com', 'community_health_worker', 'active', 'Kibera, Nairobi', 45),
            ('Peter', 'Odhiambo', '+254723456789', 'peter.o@email.com', 'nurse', 'active', 'Mathare, Nairobi', 32),
            ('Grace', 'Chebet', '+254734567890', 'grace.chebet@email.com', 'counselor', 'active', 'Kisumu Central', 28),
            ('Samuel', 'Kiprotich', '+254745678901', '', 'community_health_worker', 'active', 'Nakuru East', 51),
            ('Dorothy', 'Mwende', '+254756789012', 'dorothy@email.com', 'data_entry', 'active', 'Mombasa Island', 19),
            ('James', 'Mutua', '+254767890123', '', 'driver', 'active', 'Thika, Kiambu', 37),
            ('Agnes', 'Njoroge', '+254778901234', 'agnes@email.com', 'coordinator', 'active', 'Eldoret Town', 42),
            ('Moses', 'Otieno', '+254789012345', '', 'community_health_worker', 'inactive', 'Nyalenda, Kisumu', 15),
            ('Esther', 'Kariuki', '+254790123456', 'esther@email.com', 'nurse', 'on_leave', 'Ruiru, Kiambu', 67),
            ('Daniel', 'Adhiambo', '+254701234567', '', 'community_health_worker', 'active', 'Huruma, Nairobi', 23),
        ]
        count = 0
        for first, last, phone, email, role, status, location, tasks in volunteer_data:
            vol, created = Volunteer.objects.get_or_create(
                phone=phone,
                defaults={
                    'first_name': first, 'last_name': last,
                    'email': email, 'role': role, 'status': status,
                    'location': location, 'tasks_completed': tasks,
                }
            )
            if created:
                count += 1
        self.stdout.write(f'  Created {count} volunteers')

    def _create_messages(self):
        from django.utils import timezone
        admin = User.objects.filter(username='admin').first()

        messages_data = [
            ('sms_reminder', '+254712345678', 'Appointment Reminder',
             'Dear patient, this is a reminder that your follow-up appointment is scheduled for tomorrow at 9:00 AM. Please attend or call 0800-BRAVE if you need to reschedule.',
             'delivered'),
            ('outreach_announcement', 'All Kibera Residents', 'Free Health Camp This Weekend',
             'BraveCare is hosting a FREE health camp at Kibera Community Centre this Saturday. Services: HIV testing, blood pressure screening, malaria treatment. Bring your family!',
             'sent'),
            ('followup_notification', '+254723456789', 'Your TB Screening Results Are Ready',
             'Your tuberculosis screening results are ready for collection at the Mathare health facility. Please visit within 3 days. Call 0800-BRAVE for more information.',
             'delivered'),
            ('sms_reminder', 'Maternal Health Group', 'Antenatal Clinic Reminder',
             'This is a reminder for all expectant mothers enrolled in BraveCare: Your antenatal clinic is scheduled for Friday. Please attend with your MCH card.',
             'sent'),
            ('general', '+254734567890', 'Welcome to BraveCare Outreach',
             'Welcome to BraveCare Outreach! You have been successfully enrolled in our community health program. A community health worker will visit you within 3 days.',
             'delivered'),
        ]
        count = 0
        for mtype, recipient, subject, message, status in messages_data:
            msg, created = CommunicationMessage.objects.get_or_create(
                subject=subject,
                defaults={
                    'message_type': mtype,
                    'recipient': recipient,
                    'message': message,
                    'status': status,
                    'sent_by': admin,
                    'sent_at': timezone.now() - timedelta(days=random.randint(0, 10)),
                }
            )
            if created:
                count += 1
        self.stdout.write(f'  Created {count} messages')

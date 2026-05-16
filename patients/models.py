from django.db import models
from django.contrib.auth.models import User


def _loc_display(obj):
    """Return best available location string for any model with location fields."""
    parts = []
    for attr in ('village', 'cell', 'sector', 'district', 'province', 'country'):
        val = getattr(obj, attr, None)
        if val:
            parts.append(val.name)
    if parts:
        return ', '.join(parts)
    return getattr(obj, 'address_text', '') or getattr(obj, 'location', '') or '—'


class Patient(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    RISK_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    national_id = models.CharField(max_length=50, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    location = models.CharField(max_length=200, blank=True)   # legacy free-text
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, default='low')
    notes = models.TextField(blank=True)

    # Structured location
    country = models.ForeignKey('locations.Country', on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='+')
    province = models.ForeignKey('locations.Province', on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='+')
    district = models.ForeignKey('locations.District', on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='+')
    sector = models.ForeignKey('locations.Sector', on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='+')
    cell = models.ForeignKey('locations.Cell', on_delete=models.SET_NULL,
                             null=True, blank=True, related_name='+')
    village = models.ForeignKey('locations.Village', on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='+')
    address_text = models.CharField(max_length=300, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def display_location(self):
        return _loc_display(self)

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class Screening(models.Model):
    SCREENING_TYPE_CHOICES = [
        ('hiv', 'HIV'),
        ('malaria', 'Malaria'),
        ('tuberculosis_tb', 'Tuberculosis (TB)'),
        ('diabetes', 'Diabetes'),
        ('hypertension', 'Hypertension'),
        ('pregnancy_test', 'Pregnancy Test'),
        ('cervical_cancer', 'Cervical Cancer'),
        ('breast_cancer', 'Breast Cancer'),
        ('bmi_nutrition', 'BMI / Nutrition'),
        ('mental_health', 'Mental Health'),
        ('hepatitis_b', 'Hepatitis B'),
        ('hepatitis_c', 'Hepatitis C'),
        ('sti_screening', 'STI Screening'),
        ('cholesterol', 'Cholesterol'),
        ('sickle_cell', 'Sickle Cell'),
        ('vision_screening', 'Vision Screening'),
        ('hearing_screening', 'Hearing Screening'),
        ('covid_19', 'COVID-19'),
        ('urinalysis', 'Urinalysis'),
        ('blood_group', 'Blood Group'),
        ('anemia', 'Anemia'),
        ('child_malnutrition', 'Child Malnutrition'),
        ('family_planning', 'Family Planning'),
        ('maternal_risk_assessment', 'Maternal Risk Assessment'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('referred', 'Referred'),
        ('cancelled', 'Cancelled'),
    ]

    RISK_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='screenings')
    screening_type = models.CharField(max_length=100, choices=SCREENING_TYPE_CHOICES)
    result = models.CharField(max_length=100, blank=True, default='')
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, default='low')
    screening_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comments = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    followup_notes = models.TextField(blank=True)
    next_followup_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='screenings_performed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-screening_date', '-created_at']

    def __str__(self):
        return f"{self.patient} - {self.get_screening_type_display()} ({self.screening_date})"

    def result_badge_class(self):
        r = (self.result or '').lower().strip()
        critical = {'positive', 'critical', 'crisis', 'severe', 'disease', 'high_risk',
                    'very_high', 'severe_impairment', 'severe_loss', 'severe_malnutrition',
                    'confirmed', 'diabetic', 'stage_2', 'obese', 'abnormal'}
        safe = {'negative', 'normal', 'stable', 'immune', 'low_risk', 'counseled',
                'method_provided', 'a_positive', 'a_negative', 'b_positive', 'b_negative',
                'ab_positive', 'ab_negative', 'o_positive', 'o_negative'}
        info = {'referred', 'treated', 'indeterminate', 'declined', 'trait'}
        warning = {'prediabetic', 'suspected', 'borderline', 'needs_followup', 'moderate',
                   'mild', 'overweight', 'elevated', 'stage_1', 'moderate_malnutrition',
                   'mild_malnutrition', 'mild_impairment', 'mild_loss', 'moderate_impairment',
                   'moderate_loss', 'infection_detected', 'medium_risk', 'high'}
        if r in critical:
            return 'abnormal'
        if r in safe:
            return 'normal'
        if r in info:
            return 'referred'
        if r in warning:
            return 'medium'
        if not r or r == 'pending':
            return 'pending'
        return 'inactive'


class MaternalChildHealth(models.Model):
    SERVICE_CHOICES = [
        ('antenatal', 'Antenatal Care'),
        ('postnatal', 'Postnatal Care'),
        ('immunization', 'Immunization'),
        ('nutrition', 'Nutrition Support'),
        ('family_planning', 'Family Planning'),
        ('child_growth', 'Child Growth Monitoring'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='mch_records')
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    visit_date = models.DateField()
    next_followup_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    attended_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-visit_date']
        verbose_name = 'Maternal & Child Health Record'

    def __str__(self):
        return f"{self.patient} - {self.get_service_type_display()} ({self.visit_date})"


class FollowUp(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('missed', 'Missed'),
        ('rescheduled', 'Rescheduled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='followups')
    service = models.CharField(max_length=200)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.patient} - {self.service} ({self.due_date})"

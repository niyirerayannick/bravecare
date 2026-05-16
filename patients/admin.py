from django.contrib import admin
from .models import Patient, Screening, MaternalChildHealth, FollowUp


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'phone', 'national_id', 'location', 'risk_level', 'created_at']
    list_filter = ['risk_level', 'gender', 'created_at']
    search_fields = ['first_name', 'last_name', 'phone', 'national_id']
    date_hierarchy = 'created_at'


@admin.register(Screening)
class ScreeningAdmin(admin.ModelAdmin):
    list_display = ['patient', 'screening_type', 'result', 'risk_level', 'screening_date']
    list_filter = ['result', 'risk_level', 'screening_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'screening_type']


@admin.register(MaternalChildHealth)
class MaternalChildHealthAdmin(admin.ModelAdmin):
    list_display = ['patient', 'service_type', 'visit_date', 'next_followup_date']
    list_filter = ['service_type', 'visit_date']
    search_fields = ['patient__first_name', 'patient__last_name']


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ['patient', 'service', 'due_date', 'status']
    list_filter = ['status', 'due_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'service']

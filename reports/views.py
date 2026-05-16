from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from patients.models import Patient, Screening, FollowUp, MaternalChildHealth
from outreach.models import OutreachCampaign
from volunteers.models import Volunteer
from django.db.models import Count
from datetime import date, timedelta


@login_required
def reports_index(request):
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)

    patient_by_risk = Patient.objects.values('risk_level').annotate(count=Count('id'))
    patient_by_gender = Patient.objects.values('gender').annotate(count=Count('id'))

    followup_by_status = FollowUp.objects.values('status').annotate(count=Count('id'))

    campaign_stats = OutreachCampaign.objects.values('status').annotate(count=Count('id'))

    screening_by_result = Screening.objects.values('result').annotate(count=Count('id'))

    mch_by_service = MaternalChildHealth.objects.values('service_type').annotate(count=Count('id'))

    monthly_patients = Patient.objects.filter(
        created_at__date__gte=thirty_days_ago
    ).count()

    context = {
        'patient_by_risk': list(patient_by_risk),
        'patient_by_gender': list(patient_by_gender),
        'followup_by_status': list(followup_by_status),
        'campaign_stats': list(campaign_stats),
        'screening_by_result': list(screening_by_result),
        'mch_by_service': list(mch_by_service),
        'monthly_patients': monthly_patients,
        'total_patients': Patient.objects.count(),
        'total_screenings': Screening.objects.count(),
        'total_campaigns': OutreachCampaign.objects.count(),
        'total_volunteers': Volunteer.objects.filter(status='active').count(),
    }
    return render(request, 'reports/index.html', context)

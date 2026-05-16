from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import date, timedelta

from patients.models import Patient, Screening, FollowUp, MaternalChildHealth
from outreach.models import OutreachCampaign
from volunteers.models import Volunteer
from communication.models import CommunicationMessage


@login_required
def dashboard(request):
    today = date.today()
    week_ahead = today + timedelta(days=7)

    # KPI counts
    total_patients = Patient.objects.count()
    active_screenings = Screening.objects.filter(status='pending').count()
    upcoming_followups = FollowUp.objects.filter(
        due_date__range=[today, week_ahead],
        status='pending'
    ).count()
    active_volunteers = Volunteer.objects.filter(status='active').count()

    # Screening dashboard stats
    total_screenings = Screening.objects.count()
    positive_cases = Screening.objects.filter(
        Q(result__icontains='positive') | Q(result__icontains='diabetic') |
        Q(result__icontains='critical') | Q(result__icontains='confirmed') |
        Q(result__icontains='abnormal') | Q(result__icontains='severe')
    ).count()
    followup_required = Screening.objects.filter(status='referred').count()
    high_risk_patients = Patient.objects.filter(risk_level='high').count()

    # Month-over-month patient growth (use date field to avoid TZ issues)
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    new_patients_this_month = Patient.objects.filter(created_at__date__gte=this_month_start).count()
    new_patients_last_month = Patient.objects.filter(
        created_at__date__gte=last_month_start,
        created_at__date__lt=this_month_start
    ).count()

    # Chart data: monthly outreach performance (last 6 months)
    months_labels = []
    patients_reached_data = []
    screenings_data = []
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=30 * i)
        month_start = month_date.replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1)

        p_count = Patient.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lt=month_end
        ).count()
        s_count = Screening.objects.filter(
            screening_date__gte=month_start,
            screening_date__lt=month_end
        ).count()

        months_labels.append(month_date.strftime('%b'))
        patients_reached_data.append(p_count)
        screenings_data.append(s_count)

    # Pie chart: follow-up status
    followup_completed = FollowUp.objects.filter(status='completed').count()
    followup_pending = FollowUp.objects.filter(status='pending').count()
    followup_missed = FollowUp.objects.filter(status='missed').count()

    # Recent follow-ups for table
    recent_followups = FollowUp.objects.select_related('patient').order_by('-created_at')[:8]

    # Volunteer activity
    top_volunteers = Volunteer.objects.filter(status='active').order_by('-tasks_completed')[:5]

    # Program summary
    program_summary = {
        'preventive_care': total_screenings,
        'chronic_screening': Screening.objects.filter(
            screening_type__in=['diabetes', 'hypertension', 'cholesterol', 'anemia']
        ).count(),
        'maternal_child': MaternalChildHealth.objects.count(),
        'community_outreach': OutreachCampaign.objects.filter(
            Q(status='active') | Q(status='planned')
        ).count(),
    }

    # Recent communication
    recent_messages = CommunicationMessage.objects.all()[:3]

    context = {
        'total_patients': total_patients,
        'active_screenings': active_screenings,
        'total_screenings': total_screenings,
        'positive_cases': positive_cases,
        'followup_required': followup_required,
        'high_risk_patients': high_risk_patients,
        'upcoming_followups': upcoming_followups,
        'active_volunteers': active_volunteers,
        'new_patients_this_month': new_patients_this_month,
        'new_patients_last_month': new_patients_last_month,
        'months_labels': months_labels,
        'patients_reached_data': patients_reached_data,
        'screenings_data': screenings_data,
        'followup_completed': followup_completed,
        'followup_pending': followup_pending,
        'followup_missed': followup_missed,
        'recent_followups': recent_followups,
        'top_volunteers': top_volunteers,
        'program_summary': program_summary,
        'recent_messages': recent_messages,
        'active_campaigns': OutreachCampaign.objects.filter(status='active')[:3],
    }
    return render(request, 'core/dashboard.html', context)

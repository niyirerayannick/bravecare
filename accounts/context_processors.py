def user_role_context(request):
    """Inject role booleans, profile, and countries into every template context."""
    from locations.models import Country
    countries = list(Country.objects.values('id', 'name', 'phone_code', 'iso_code'))

    if not request.user.is_authenticated:
        return {
            'user_role': '',
            'user_profile': None,
            'is_admin': False,
            'is_coordinator': False,
            'is_healthcare_worker': False,
            'is_volunteer': False,
            'countries': countries,
        }

    try:
        profile = request.user.profile
        role = profile.role
    except Exception:
        profile = None
        role = ''

    is_admin = role in ('system_administrator', 'admin') or request.user.is_superuser

    return {
        'user_role': role,
        'user_profile': profile,
        'is_admin': is_admin,
        'is_coordinator': role == 'coordinator',
        'is_healthcare_worker': role == 'healthcare_worker',
        'is_volunteer': role == 'volunteer',
        'can_manage_patients': is_admin or role in ('coordinator', 'healthcare_worker'),
        'can_manage_outreach': is_admin or role == 'coordinator',
        'can_manage_volunteers': is_admin or role == 'coordinator',
        'can_view_reports': is_admin or role == 'coordinator',
        'can_communicate': is_admin or role == 'coordinator',
        'can_manage_screening': is_admin or role in ('coordinator', 'healthcare_worker'),
        'can_manage_mch': is_admin or role == 'healthcare_worker',
        'countries': countries,
    }

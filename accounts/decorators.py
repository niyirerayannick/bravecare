from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def _get_role(user):
    """Return the user's role string, treating superusers as system_administrator."""
    if user.is_superuser:
        return 'system_administrator'
    try:
        return user.profile.role
    except Exception:
        return ''


def role_required(*allowed_roles):
    """Restrict a view to users whose profile.role is in allowed_roles."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f'/accounts/login/?next={request.path}')
            role = _get_role(request.user)
            # Admins (both legacy 'admin' and 'system_administrator') pass everything
            if role in ('system_administrator', 'admin') or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if role in allowed_roles:
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden(
                '<h2 style="font-family:sans-serif;padding:2rem;">403 — Access Denied</h2>'
                '<p style="font-family:sans-serif;padding:0 2rem;">You do not have permission to access this page.</p>'
            )
        return wrapper
    return decorator


def admin_required(view_func):
    """Shortcut: restrict to System Administrator only."""
    return role_required('system_administrator', 'admin')(view_func)

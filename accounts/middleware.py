from django.shortcuts import redirect
from django.urls import reverse

# URLs exempt from the force-change-password redirect
_EXEMPT = {
    '/accounts/force-change-password/',
    '/accounts/logout/',
    '/accounts/login/',
}


class ForcePasswordChangeMiddleware:
    """
    Redirect any authenticated user whose profile.must_change_password is True
    to the force-change-password page before they can access anything else.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and request.path not in _EXEMPT
            and not request.path.startswith('/admin/')
            and not request.path.startswith('/static/')
        ):
            try:
                if request.user.profile.must_change_password:
                    return redirect('/accounts/force-change-password/')
            except Exception:
                pass
        return self.get_response(request)

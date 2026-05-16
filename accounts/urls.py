from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────
    path('login/',                   views.login_view,                name='login'),
    path('logout/',                  views.logout_view,               name='logout'),
    path('otp-verify/',              views.otp_verify_view,           name='otp_verify'),
    # ── Forgot / reset password ────────────────────────────────────────
    path('forgot-password/',         views.forgot_password_view,      name='forgot_password'),
    path('forgot-password/verify/',  views.forgot_otp_view,           name='forgot_otp'),
    path('forgot-password/reset/',   views.reset_password_view,       name='reset_password'),
    path('forgot-password/success/', views.reset_success_view,        name='reset_success'),
    # ── Profile & password ─────────────────────────────────────────────
    path('profile/',                 views.profile_view,              name='profile'),
    path('change-password/',         views.change_password_view,      name='change_password'),
    path('force-change-password/',   views.force_change_password_view, name='force_change_password'),
    # ── User management (admin only) ───────────────────────────────────
    path('users/',                             views.user_list,                name='user_list'),
    path('users/add/',                         views.user_add,                 name='user_add'),
    path('users/<int:pk>/edit/',               views.user_edit,                name='user_edit'),
    path('users/<int:pk>/json/',               views.user_json,                name='user_json'),
    path('users/<int:pk>/toggle-status/',      views.user_toggle_status,       name='user_toggle_status'),
    path('users/<int:pk>/reset-password/',     views.user_reset_password,      name='user_reset_password'),
    path('users/<int:pk>/send-login-details/', views.user_send_login_details,  name='user_send_login_details'),
    path('users/<int:pk>/force-password-change/', views.user_force_password_change, name='user_force_password_change'),
]

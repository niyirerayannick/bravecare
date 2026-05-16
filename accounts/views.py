import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .decorators import admin_required
from .email_utils import (
    create_otp, can_resend_otp,
    send_welcome_email, send_login_otp,
    send_forgot_password_otp, send_password_changed_email,
)
from .forms import (
    UserCreateForm, UserEditForm, ResetPasswordForm, ChangePasswordForm,
    ForceChangePasswordForm, OTPVerifyForm, ForgotPasswordForm, ResetPasswordConfirmForm,
)
from .models import UserProfile, EmailOTP
from patients.views import _apply_location, _location_json

logger = logging.getLogger(__name__)


def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def _form_errors(form):
    return {k: [str(e) for e in v] for k, v in form.errors.items()}


def _login_url(request):
    return request.build_absolute_uri('/accounts/login/')


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTH — LOGIN / LOGOUT / OTP
# ═══════════════════════════════════════════════════════════════════════════════

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'registration/login.html')

        if not user.is_active:
            messages.error(request, 'Your account is inactive. Please contact your administrator.')
            return render(request, 'registration/login.html')

        # Check if 2FA is enabled for this user
        try:
            two_fa = user.profile.two_factor_enabled
        except UserProfile.DoesNotExist:
            two_fa = True

        if two_fa and user.email:
            # Generate OTP and store pending user in session
            otp = create_otp(user, EmailOTP.PURPOSE_LOGIN)
            send_login_otp(user, otp)
            request.session['otp_pending_user_id'] = user.pk
            request.session['otp_pending_next'] = request.GET.get('next', '/')
            return redirect('accounts:otp_verify')
        else:
            # No 2FA — log in directly
            login(request, user)
            logger.info("Login (no 2FA): %s", user.username)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)

    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def otp_verify_view(request):
    """Step 2 of login — verify the emailed OTP."""
    user_id = request.session.get('otp_pending_user_id')
    if not user_id:
        return redirect('accounts:login')

    user = get_object_or_404(User, pk=user_id)
    email_hint = _mask_email(user.email)

    if request.method == 'POST':
        action = request.POST.get('action')

        # ── Resend ──────────────────────────────────────────────────────
        if action == 'resend':
            if can_resend_otp(user, EmailOTP.PURPOSE_LOGIN):
                otp = create_otp(user, EmailOTP.PURPOSE_LOGIN)
                send_login_otp(user, otp)
                messages.success(request, 'A new verification code has been sent.')
            else:
                messages.error(request, f'Please wait {settings.OTP_RESEND_COOLDOWN} seconds before requesting a new code.')
            return render(request, 'accounts/otp_verify.html', {'email_hint': email_hint, 'form': OTPVerifyForm()})

        # ── Verify ──────────────────────────────────────────────────────
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            otp = (
                EmailOTP.objects
                .filter(user=user, purpose=EmailOTP.PURPOSE_LOGIN, is_used=False)
                .order_by('-created_at')
                .first()
            )

            if otp is None:
                messages.error(request, 'No active verification code found. Please request a new one.')
                return render(request, 'accounts/otp_verify.html', {'email_hint': email_hint, 'form': form})

            if timezone.now() >= otp.expires_at:
                messages.error(request, 'Your verification code has expired. Please request a new one.')
                return render(request, 'accounts/otp_verify.html', {'email_hint': email_hint, 'form': form})

            if otp.attempts >= settings.OTP_MAX_ATTEMPTS:
                messages.error(request, 'Too many incorrect attempts. Please request a new code.')
                return render(request, 'accounts/otp_verify.html', {'email_hint': email_hint, 'form': form})

            if otp.code != code:
                otp.attempts += 1
                otp.save(update_fields=['attempts'])
                remaining = settings.OTP_MAX_ATTEMPTS - otp.attempts
                if remaining > 0:
                    messages.error(request, f'Incorrect code. {remaining} attempt{"s" if remaining != 1 else ""} remaining.')
                else:
                    messages.error(request, 'Too many incorrect attempts. Please request a new code.')
                return render(request, 'accounts/otp_verify.html', {'email_hint': email_hint, 'form': form})

            # Success — mark OTP used and log the user in
            otp.is_used = True
            otp.save(update_fields=['is_used'])
            next_url = request.session.pop('otp_pending_next', '/')
            request.session.pop('otp_pending_user_id', None)
            login(request, user)
            logger.info("Login (2FA OK): %s", user.username)
            return redirect(next_url)

        return render(request, 'accounts/otp_verify.html', {'email_hint': email_hint, 'form': form})

    return render(request, 'accounts/otp_verify.html', {
        'email_hint': email_hint,
        'form': OTPVerifyForm(),
    })


# ═══════════════════════════════════════════════════════════════════════════════
#  FORGOT PASSWORD
# ═══════════════════════════════════════════════════════════════════════════════

def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email, is_active=True)
                if can_resend_otp(user, EmailOTP.PURPOSE_RESET):
                    otp = create_otp(user, EmailOTP.PURPOSE_RESET)
                    send_forgot_password_otp(user, otp)
                # Store in session whether email was found or not — always show same page
                request.session['reset_user_id'] = user.pk
            except User.DoesNotExist:
                pass  # Do not reveal whether email exists
            # Always redirect to OTP page (prevents user enumeration)
            return redirect('accounts:forgot_otp')
        return render(request, 'accounts/forgot_password.html', {'form': form})

    return render(request, 'accounts/forgot_password.html', {'form': ForgotPasswordForm()})


def forgot_otp_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    user_id = request.session.get('reset_user_id')
    # Show the page even if no user_id (prevents enumeration)
    user = User.objects.filter(pk=user_id).first() if user_id else None
    email_hint = _mask_email(user.email) if user else '••••@••••'

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'resend':
            if user and can_resend_otp(user, EmailOTP.PURPOSE_RESET):
                otp = create_otp(user, EmailOTP.PURPOSE_RESET)
                send_forgot_password_otp(user, otp)
                messages.success(request, 'A new reset code has been sent.')
            else:
                messages.error(request, f'Please wait {settings.OTP_RESEND_COOLDOWN} seconds before requesting a new code.')
            return render(request, 'accounts/forgot_otp.html', {'email_hint': email_hint, 'form': OTPVerifyForm()})

        form = OTPVerifyForm(request.POST)
        if form.is_valid() and user:
            code = form.cleaned_data['code']
            otp = (
                EmailOTP.objects
                .filter(user=user, purpose=EmailOTP.PURPOSE_RESET, is_used=False)
                .order_by('-created_at')
                .first()
            )

            if otp is None or timezone.now() >= otp.expires_at:
                messages.error(request, 'Code expired or not found. Please request a new one.')
                return render(request, 'accounts/forgot_otp.html', {'email_hint': email_hint, 'form': form})

            if otp.attempts >= settings.OTP_MAX_ATTEMPTS:
                messages.error(request, 'Too many incorrect attempts. Please start over.')
                return render(request, 'accounts/forgot_otp.html', {'email_hint': email_hint, 'form': form})

            if otp.code != code:
                otp.attempts += 1
                otp.save(update_fields=['attempts'])
                remaining = settings.OTP_MAX_ATTEMPTS - otp.attempts
                if remaining > 0:
                    messages.error(request, f'Incorrect code. {remaining} attempt{"s" if remaining != 1 else ""} remaining.')
                else:
                    messages.error(request, 'Too many incorrect attempts. Please start over.')
                return render(request, 'accounts/forgot_otp.html', {'email_hint': email_hint, 'form': form})

            otp.is_used = True
            otp.save(update_fields=['is_used'])
            request.session['reset_verified_user_id'] = user.pk
            request.session.pop('reset_user_id', None)
            return redirect('accounts:reset_password')

        messages.error(request, 'Please enter a valid 6-digit code.')
        return render(request, 'accounts/forgot_otp.html', {'email_hint': email_hint, 'form': form})

    return render(request, 'accounts/forgot_otp.html', {
        'email_hint': email_hint,
        'form': OTPVerifyForm(),
    })


def reset_password_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    user_id = request.session.get('reset_verified_user_id')
    if not user_id:
        return redirect('accounts:forgot_password')

    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        form = ResetPasswordConfirmForm(request.POST, user=user)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            try:
                user.profile.must_change_password = False
                user.profile.save(update_fields=['must_change_password'])
            except UserProfile.DoesNotExist:
                pass
            request.session.pop('reset_verified_user_id', None)
            send_password_changed_email(user)
            logger.info("Password reset via forgot-password: %s", user.username)
            return redirect('accounts:reset_success')
        return render(request, 'accounts/reset_password.html', {'form': form})

    return render(request, 'accounts/reset_password.html', {'form': ResetPasswordConfirmForm(user=user)})


def reset_success_view(request):
    return render(request, 'accounts/reset_success.html')


# ═══════════════════════════════════════════════════════════════════════════════
#  PROFILE & PASSWORD CHANGE
# ═══════════════════════════════════════════════════════════════════════════════

@login_required
def profile_view(request):
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = None
    return render(request, 'accounts/profile.html', {'user_profile': user_profile})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            update_session_auth_hash(request, request.user)
            try:
                request.user.profile.must_change_password = False
                request.user.profile.save(update_fields=['must_change_password'])
            except UserProfile.DoesNotExist:
                pass
            send_password_changed_email(request.user)
            if _is_ajax(request):
                return JsonResponse({'success': True, 'message': 'Password changed successfully.'})
            messages.success(request, 'Password changed successfully.')
            return redirect('accounts:profile')
        if _is_ajax(request):
            return JsonResponse({'success': False, 'errors': _form_errors(form)}, status=400)
    return redirect('accounts:profile')


@login_required
def force_change_password_view(request):
    """Shown when must_change_password=True. User cannot proceed until they change it."""
    if request.method == 'POST':
        form = ForceChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            update_session_auth_hash(request, request.user)
            request.user.profile.must_change_password = False
            request.user.profile.save(update_fields=['must_change_password'])
            send_password_changed_email(request.user)
            messages.success(request, 'Password updated. Welcome to BraveCare Outreach!')
            logger.info("Force password change completed: %s", request.user.username)
            return redirect('core:dashboard')
        return render(request, 'accounts/force_change_password.html', {'form': form})
    return render(request, 'accounts/force_change_password.html', {'form': ForceChangePasswordForm(user=request.user)})


# ═══════════════════════════════════════════════════════════════════════════════
#  USER MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

@admin_required
def user_list(request):
    query         = request.GET.get('q', '')
    role_filter   = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')

    users = User.objects.select_related('profile').all().order_by('-date_joined')

    if query:
        users = users.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) |
            Q(username__icontains=query)   | Q(email__icontains=query) |
            Q(profile__phone__icontains=query)
        )
    if role_filter:
        users = users.filter(profile__role=role_filter)
    if status_filter:
        users = users.filter(profile__status=status_filter)

    context = {
        'users':        users,
        'query':        query,
        'role_filter':  role_filter,
        'status_filter': status_filter,
        'total_count':  User.objects.count(),
        'active_count': User.objects.filter(is_active=True).count(),
        'admin_count':  UserProfile.objects.filter(role__in=['system_administrator', 'admin']).count(),
        'role_choices': UserProfile.ROLE_CHOICES,
    }
    return render(request, 'accounts/users.html', context)


@admin_required
def user_add(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            temp_password = form.get_password()
            user = User.objects.create_user(
                username   = d['username'],
                email      = d.get('email', ''),
                password   = temp_password,
                first_name = d['first_name'],
                last_name  = d['last_name'],
                is_active  = (d['status'] == 'active'),
            )
            profile = UserProfile.objects.create(
                user                = user,
                role                = d['role'],
                phone               = d.get('phone', ''),
                status              = d['status'],
                must_change_password = True,
                two_factor_enabled  = True,
            )
            _apply_location(profile, request.POST)
            profile.save()

            # Send welcome email (non-blocking — errors are logged, not raised)
            sent = send_welcome_email(user, temp_password, _login_url(request))
            logger.info("User created: %s (email sent: %s)", user.username, sent)

            if _is_ajax(request):
                return JsonResponse({'success': True, 'message': f'User {user.get_full_name()} created. Login details sent to {user.email}.'})
            messages.success(request, f'User {user.get_full_name()} created. Login details sent to {user.email}.')
            return redirect('accounts:user_list')
        if _is_ajax(request):
            return JsonResponse({'success': False, 'errors': _form_errors(form)}, status=400)
    return redirect('accounts:user_list')


@admin_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserEditForm(request.POST, user_instance=user)
        if form.is_valid():
            d = form.cleaned_data
            user.first_name = d['first_name']
            user.last_name  = d['last_name']
            user.username   = d['username']
            user.email      = d.get('email', '')
            user.is_active  = (d['status'] == 'active')
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role   = d['role']
            profile.phone  = d.get('phone', '')
            profile.status = d['status']
            _apply_location(profile, request.POST)
            profile.save()
            if _is_ajax(request):
                return JsonResponse({'success': True, 'message': f'{user.get_full_name()} updated.'})
            messages.success(request, 'User updated.')
            return redirect('accounts:user_list')
        if _is_ajax(request):
            return JsonResponse({'success': False, 'errors': _form_errors(form)}, status=400)
    return redirect('accounts:user_list')


@admin_required
def user_json(request, pk):
    user = get_object_or_404(User, pk=pk)
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = None
    data = {
        'first_name':  user.first_name,
        'last_name':   user.last_name,
        'username':    user.username,
        'email':       user.email,
        'phone':       profile.phone if profile else '',
        'role':        profile.role if profile else 'healthcare_worker',
        'status':      profile.status if profile else 'active',
        'must_change_password': profile.must_change_password if profile else False,
        'email_verified':       profile.email_verified if profile else False,
        'two_factor_enabled':   profile.two_factor_enabled if profile else True,
        'last_login':  user.last_login.strftime('%b %d, %Y %H:%M') if user.last_login else '',
        'date_joined': user.date_joined.strftime('%b %d, %Y'),
    }
    if profile:
        data.update(_location_json(profile))
    return JsonResponse(data)


@admin_required
def user_toggle_status(request, pk):
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=405)
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        return JsonResponse({'success': False, 'message': 'You cannot deactivate your own account.'}, status=400)
    try:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        new_status = 'inactive' if profile.status == 'active' else 'active'
        UserProfile.objects.filter(pk=profile.pk).update(status=new_status)
        user.is_active = (new_status == 'active')
        user.save(update_fields=['is_active'])
        label = 'activated' if new_status == 'active' else 'deactivated'
        return JsonResponse({'success': True, 'message': f'{user.get_full_name()} {label}.', 'new_status': new_status})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@admin_required
def user_reset_password(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            try:
                user.profile.must_change_password = True
                user.profile.save(update_fields=['must_change_password'])
            except UserProfile.DoesNotExist:
                pass
            if _is_ajax(request):
                return JsonResponse({'success': True, 'message': f'Password reset for {user.get_full_name()}. They will be prompted to change it on next login.'})
            messages.success(request, 'Password reset successfully.')
            return redirect('accounts:user_list')
        if _is_ajax(request):
            return JsonResponse({'success': False, 'errors': _form_errors(form)}, status=400)
    return redirect('accounts:user_list')


@admin_required
@require_POST
def user_send_login_details(request, pk):
    """Re-send welcome email with a freshly generated temporary password."""
    user = get_object_or_404(User, pk=pk)
    if not user.email:
        return JsonResponse({'success': False, 'message': 'This user has no email address on file.'}, status=400)

    from .forms import generate_temp_password
    temp_password = generate_temp_password()
    user.set_password(temp_password)
    user.save()
    try:
        user.profile.must_change_password = True
        user.profile.save(update_fields=['must_change_password'])
    except UserProfile.DoesNotExist:
        pass

    sent = send_welcome_email(user, temp_password, _login_url(request))
    if sent:
        logger.info("Login details re-sent for %s by %s", user.username, request.user.username)
        return JsonResponse({'success': True, 'message': f'Login details sent to {user.email}.'})
    return JsonResponse({'success': False, 'message': 'Email could not be sent. Check your email settings.'}, status=500)


@admin_required
@require_POST
def user_force_password_change(request, pk):
    """Flag a user's account to require a password change on next login."""
    user = get_object_or_404(User, pk=pk)
    try:
        user.profile.must_change_password = True
        user.profile.save(update_fields=['must_change_password'])
        return JsonResponse({'success': True, 'message': f'{user.get_full_name()} will be prompted to change password on next login.'})
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User profile not found.'}, status=400)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mask_email(email: str) -> str:
    """Return a privacy-masked version of an email address: u••••@d••••.com"""
    if not email or '@' not in email:
        return '••••@••••'
    local, domain = email.split('@', 1)
    masked_local  = local[0] + '••••' if len(local) > 1 else '••••'
    parts = domain.rsplit('.', 1)
    masked_domain = parts[0][0] + '••••.' + parts[1] if len(parts) == 2 else '••••'
    return f"{masked_local}@{masked_domain}"

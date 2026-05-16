import secrets
import string

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import UserProfile


def generate_temp_password(length=14):
    """Generate a cryptographically strong temporary password."""
    alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits + '!@#$%&'
    while True:
        pwd = ''.join(secrets.choice(alphabet) for _ in range(length))
        # Ensure at least one of each required character class
        if (any(c.isupper() for c in pwd)
                and any(c.islower() for c in pwd)
                and any(c.isdigit() for c in pwd)
                and any(c in '!@#$%&' for c in pwd)):
            return pwd


class UserCreateForm(forms.Form):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First name'}))
    last_name  = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last name'}))
    username   = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}))
    email      = forms.EmailField(required=True,  widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'email@example.com'}))
    phone      = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+250…'}))
    role       = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    status     = forms.ChoiceField(choices=UserProfile.STATUS_CHOICES, initial='active', widget=forms.Select(attrs={'class': 'form-select'}))
    # Password optional — leave blank to auto-generate
    password   = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Leave blank to auto-generate'}))

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken.')
        return username

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password', '').strip()
        if pw:
            try:
                validate_password(pw)
            except ValidationError as e:
                self.add_error('password', e)
        return cleaned

    def get_password(self):
        """Return provided password or a newly generated one."""
        pw = self.cleaned_data.get('password', '').strip()
        return pw if pw else generate_temp_password()


class UserEditForm(forms.Form):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name  = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input'}))
    username   = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input'}))
    email      = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-input'}))
    phone      = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))
    role       = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    status     = forms.ChoiceField(choices=UserProfile.STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    def __init__(self, *args, user_instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user_instance = user_instance

    def clean_username(self):
        username = self.cleaned_data['username']
        qs = User.objects.filter(username=username)
        if self._user_instance:
            qs = qs.exclude(pk=self._user_instance.pk)
        if qs.exists():
            raise ValidationError('This username is already taken.')
        return username


class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'New password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm new password'})
    )

    def clean(self):
        cleaned = super().clean()
        pw  = cleaned.get('new_password')
        cpw = cleaned.get('confirm_password')
        if pw and cpw and pw != cpw:
            self.add_error('confirm_password', 'Passwords do not match.')
        if pw:
            try:
                validate_password(pw)
            except ValidationError as e:
                self.add_error('new_password', e)
        return cleaned


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Current password'})
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'New password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm new password'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user

    def clean_current_password(self):
        pw = self.cleaned_data['current_password']
        if self._user and not self._user.check_password(pw):
            raise ValidationError('Current password is incorrect.')
        return pw

    def clean(self):
        cleaned = super().clean()
        pw  = cleaned.get('new_password')
        cpw = cleaned.get('confirm_password')
        if pw and cpw and pw != cpw:
            self.add_error('confirm_password', 'Passwords do not match.')
        if pw:
            try:
                validate_password(pw, user=self._user)
            except ValidationError as e:
                self.add_error('new_password', e)
        return cleaned


class ForceChangePasswordForm(forms.Form):
    """Used when must_change_password=True on first login."""
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'New password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm new password'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user

    def clean(self):
        cleaned = super().clean()
        pw  = cleaned.get('new_password')
        cpw = cleaned.get('confirm_password')
        if pw and cpw and pw != cpw:
            self.add_error('confirm_password', 'Passwords do not match.')
        if pw:
            try:
                validate_password(pw, user=self._user)
            except ValidationError as e:
                self.add_error('new_password', e)
        return cleaned


class OTPVerifyForm(forms.Form):
    code = forms.CharField(
        max_length=6, min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-input text-center text-2xl tracking-widest font-mono',
            'placeholder': '000000',
            'inputmode': 'numeric',
            'autocomplete': 'one-time-code',
            'maxlength': '6',
        })
    )

    def clean_code(self):
        code = self.cleaned_data['code'].strip()
        if not code.isdigit():
            raise ValidationError('OTP must be 6 digits.')
        return code


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your account email address',
        })
    )


class ResetPasswordConfirmForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'New password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm new password'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = user

    def clean(self):
        cleaned = super().clean()
        pw  = cleaned.get('new_password')
        cpw = cleaned.get('confirm_password')
        if pw and cpw and pw != cpw:
            self.add_error('confirm_password', 'Passwords do not match.')
        if pw:
            try:
                validate_password(pw, user=self._user)
            except ValidationError as e:
                self.add_error('new_password', e)
        return cleaned

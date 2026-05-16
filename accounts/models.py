from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from patients.models import _loc_display


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('system_administrator', 'System Administrator'),
        ('coordinator', 'Outreach Coordinator'),
        ('healthcare_worker', 'Healthcare Worker'),
        ('volunteer', 'Volunteer'),
        ('admin', 'Administrator'),  # legacy — kept for existing seed data
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='healthcare_worker')
    phone = models.CharField(max_length=30, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    avatar_initials = models.CharField(max_length=3, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Security flags
    must_change_password = models.BooleanField(default=False)
    email_verified       = models.BooleanField(default=False)
    two_factor_enabled   = models.BooleanField(default=True)

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

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        name = self.user.get_full_name() or self.user.username
        parts = name.split()
        self.avatar_initials = ''.join([p[0].upper() for p in parts[:2]])
        active = (self.status == 'active')
        if self.user.is_active != active:
            self.user.is_active = active
            self.user.save(update_fields=['is_active'])
        super().save(*args, **kwargs)

    def is_admin_role(self):
        return self.role in ('system_administrator', 'admin') or self.user.is_superuser

    def display_location(self):
        return _loc_display(self)


class EmailOTP(models.Model):
    PURPOSE_LOGIN    = 'login_verification'
    PURPOSE_RESET    = 'password_reset'
    PURPOSE_VERIFY   = 'email_verification'

    PURPOSE_CHOICES = [
        (PURPOSE_LOGIN,  'Login Verification'),
        (PURPOSE_RESET,  'Password Reset'),
        (PURPOSE_VERIFY, 'Email Verification'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    code       = models.CharField(max_length=6)
    purpose    = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    is_used    = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    attempts   = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def is_valid(self):
        return (
            not self.is_used
            and self.attempts < 3
            and timezone.now() < self.expires_at
        )

    def __str__(self):
        return f"OTP({self.purpose}) for {self.user.username} [{self.code}]"

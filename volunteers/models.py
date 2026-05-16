from django.db import models
from patients.models import _loc_display


class Volunteer(models.Model):
    ROLE_CHOICES = [
        ('community_health_worker', 'Community Health Worker'),
        ('nurse', 'Nurse'),
        ('doctor', 'Doctor'),
        ('counselor', 'Counselor'),
        ('data_entry', 'Data Entry Clerk'),
        ('driver', 'Driver'),
        ('coordinator', 'Field Coordinator'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    location = models.CharField(max_length=200, blank=True)   # legacy
    tasks_completed = models.PositiveIntegerField(default=0)
    joined_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

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

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def display_location(self):
        return _loc_display(self)

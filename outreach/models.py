from django.db import models
from django.contrib.auth.models import User
from patients.models import _loc_display


class OutreachCampaign(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True)   # legacy
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    target_population = models.PositiveIntegerField(default=0)
    reached_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
        return self.title

    def display_location(self):
        return _loc_display(self)

    @property
    def progress_percent(self):
        if self.target_population == 0:
            return 0
        return min(int((self.reached_count / self.target_population) * 100), 100)

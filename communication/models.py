from django.db import models
from django.contrib.auth.models import User


class CommunicationMessage(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('sms_reminder', 'SMS Reminder'),
        ('outreach_announcement', 'Outreach Announcement'),
        ('followup_notification', 'Follow-up Notification'),
        ('general', 'General Message'),
        ('emergency', 'Emergency Alert'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]

    recipient = models.CharField(max_length=200)
    message_type = models.CharField(max_length=30, choices=MESSAGE_TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} → {self.recipient}"

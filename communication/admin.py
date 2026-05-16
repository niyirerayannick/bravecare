from django.contrib import admin
from .models import CommunicationMessage


@admin.register(CommunicationMessage)
class CommunicationMessageAdmin(admin.ModelAdmin):
    list_display = ['subject', 'recipient', 'message_type', 'status', 'sent_at']
    list_filter = ['message_type', 'status', 'sent_at']
    search_fields = ['subject', 'recipient', 'message']

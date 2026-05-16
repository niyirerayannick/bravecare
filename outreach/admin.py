from django.contrib import admin
from .models import OutreachCampaign


@admin.register(OutreachCampaign)
class OutreachCampaignAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'start_date', 'end_date', 'status', 'reached_count']
    list_filter = ['status', 'start_date']
    search_fields = ['title', 'location']

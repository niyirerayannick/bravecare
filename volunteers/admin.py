from django.contrib import admin
from .models import Volunteer


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'role', 'phone', 'status', 'tasks_completed']
    list_filter = ['status', 'role']
    search_fields = ['first_name', 'last_name', 'phone']

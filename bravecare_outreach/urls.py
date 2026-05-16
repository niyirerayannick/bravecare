from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('core.urls')),
    path('patients/', include('patients.urls')),
    path('outreach/', include('outreach.urls')),
    path('volunteers/', include('volunteers.urls')),
    path('communication/', include('communication.urls')),
    path('reports/', include('reports.urls')),
    path('locations/', include('locations.urls')),
]

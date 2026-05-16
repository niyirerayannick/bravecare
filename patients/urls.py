from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    # Patients
    path('', views.patient_list, name='list'),
    path('add/', views.patient_add, name='add'),
    path('<int:pk>/', views.patient_detail, name='detail'),
    path('<int:pk>/edit/', views.patient_edit, name='edit'),
    path('<int:pk>/json/', views.patient_json, name='json'),

    # Patient autocomplete
    path('autocomplete/', views.patient_autocomplete, name='autocomplete'),

    # Screenings
    path('screenings/', views.screening_list, name='screening_list'),
    path('screenings/add/', views.screening_add, name='screening_add'),
    path('screenings/<int:pk>/edit/', views.screening_edit, name='screening_edit'),
    path('screenings/<int:pk>/json/', views.screening_json, name='screening_json'),
    path('screenings/export/csv/', views.screening_export_csv, name='screening_export_csv'),
    path('screenings/export/excel/', views.screening_export_excel, name='screening_export_excel'),
    path('screenings/export/pdf/', views.screening_export_pdf, name='screening_export_pdf'),

    # Follow-ups
    path('followups/', views.followup_list, name='followup_list'),
    path('followups/add/', views.followup_add, name='followup_add'),
    path('followups/<int:pk>/edit/', views.followup_edit, name='followup_edit'),
    path('followups/<int:pk>/json/', views.followup_json, name='followup_json'),

    # MCH
    path('mch/add/', views.mch_add, name='mch_add'),
    path('mch/<int:pk>/edit/', views.mch_edit, name='mch_edit'),
    path('mch/<int:pk>/json/', views.mch_json, name='mch_json'),
]

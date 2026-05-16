from django.urls import path
from . import views

app_name = 'locations'

urlpatterns = [
    path('countries/', views.countries_list, name='countries'),
    path('provinces/', views.provinces, name='provinces'),
    path('districts/', views.districts, name='districts'),
    path('sectors/', views.sectors, name='sectors'),
    path('cells/', views.cells, name='cells'),
    path('villages/', views.villages, name='villages'),
]

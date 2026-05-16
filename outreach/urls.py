from django.urls import path
from . import views

app_name = 'outreach'

urlpatterns = [
    path('', views.campaign_list, name='list'),
    path('add/', views.campaign_add, name='add'),
    path('<int:pk>/', views.campaign_detail, name='detail'),
    path('<int:pk>/edit/', views.campaign_edit, name='edit'),
    path('<int:pk>/json/', views.campaign_json, name='json'),
]

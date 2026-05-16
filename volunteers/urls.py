from django.urls import path
from . import views

app_name = 'volunteers'

urlpatterns = [
    path('', views.volunteer_list, name='list'),
    path('add/', views.volunteer_add, name='add'),
    path('<int:pk>/edit/', views.volunteer_edit, name='edit'),
    path('<int:pk>/json/', views.volunteer_json, name='json'),
]

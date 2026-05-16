from django.urls import path
from . import views

app_name = 'communication'

urlpatterns = [
    path('', views.communication_center, name='center'),
    path('add/', views.message_add, name='add'),
    path('<int:pk>/edit/', views.message_edit, name='edit'),
    path('<int:pk>/json/', views.message_json, name='json'),
]

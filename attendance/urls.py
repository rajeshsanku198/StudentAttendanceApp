from django.urls import path

from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.home, name='home'),
    path('students/register/', views.register_student, name='register_student'),
    path('attendance/daily/', views.attendance_daily, name='attendance_daily'),
]

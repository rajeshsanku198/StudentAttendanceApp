from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('attendance/take/<str:class_name>/', views.take_attendance, name='take_attendance'),
    path('attendance/process/', views.process_attendance, name='process_attendance'),
    path('students/register/', views.register_student, name='register_student'),
    path('attendance/daily/', views.attendance_daily, name='attendance_daily'),
]
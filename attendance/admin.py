print("Attendance admin loaded")
from django.contrib import admin

from .models import AttendanceRecord, Student

admin.site.site_header = "Vitality Administration"
admin.site.site_title = "Vitality Admin Portal"
admin.site.index_title = "Welcome to Vitality Dashboard"


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'first_name', 'last_name', 'class_name', 'email', 'phone')
    search_fields = ('student_id', 'first_name', 'last_name', 'class_name')
    list_filter = ('class_name',)


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'note')
    list_filter = ('status', 'date')
    search_fields = ('student__student_id', 'student__first_name', 'student__last_name')
    date_hierarchy = 'date'

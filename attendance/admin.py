print("Attendance admin loaded")
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import AttendanceRecord, Student, Teacher

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


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'assigned_classes', 'phone')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'assigned_classes')


class TeacherInline(admin.StackedInline):
    model = Teacher
    can_delete = False
    verbose_name_plural = 'Teacher Profile'


class CustomUserAdmin(BaseUserAdmin):
    inlines = (TeacherInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

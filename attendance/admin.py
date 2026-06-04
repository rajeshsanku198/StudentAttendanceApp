from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'first_name', 'last_name', 'class_name', 'email', 'phone')
    search_fields = ('student_id', 'first_name', 'last_name', 'class_name')
    list_filter = ('class_name',)

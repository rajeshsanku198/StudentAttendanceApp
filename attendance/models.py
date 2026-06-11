from django.contrib.auth.models import User
from django.db import models


class Student(models.Model):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    student_id = models.CharField(max_length=30, unique=True)
    class_name = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    face_image = models.ImageField(upload_to='student_faces/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.student_id})'


class AttendanceRecord(models.Model):
    PRESENT = 'present'
    ABSENT = 'absent'

    STATUS_CHOICES = [
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', 'student__student_id']
        constraints = [
            models.UniqueConstraint(fields=['student', 'date'], name='unique_student_attendance_date'),
        ]

    def __str__(self):
        return f'{self.student.student_id} - {self.date} - {self.get_status_display()}'


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    assigned_classes = models.CharField(max_length=500, help_text='Comma-separated class names, e.g. CS-301,CS-302')
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.user.username})'

    def get_class_list(self):
        return [c.strip() for c in self.assigned_classes.split(',') if c.strip()]

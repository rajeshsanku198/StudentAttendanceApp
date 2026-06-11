import base64
import json
import os
import tempfile

import cv2
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .forms import AttendanceFilterForm, AttendanceRecordForm, StudentRegistrationForm
from .models import AttendanceRecord, Student, Teacher


def home(request):
    return render(request, 'attendance/home.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('attendance:teacher_dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'attendance:teacher_dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'attendance/login.html')


def logout_view(request):
    logout(request)
    return redirect('attendance:home')


@login_required(login_url='attendance:login')
def teacher_dashboard(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, 'No teacher profile found for this account.')
        return redirect('attendance:home')

    classes = teacher.get_class_list()
    class_data = []
    today = __import__('datetime').date.today()

    for cls in classes:
        students = Student.objects.filter(class_name=cls)
        total = students.count()
        present_today = AttendanceRecord.objects.filter(
            student__class_name=cls, date=today, status=AttendanceRecord.PRESENT
        ).count()

        total_records = AttendanceRecord.objects.filter(
            student__class_name=cls
        ).count()

        class_data.append({
            'name': cls,
            'total_students': total,
            'present_today': present_today,
            'absent_today': total - present_today,
            'total_records': total_records,
        })

    return render(request, 'attendance/teacher_dashboard.html', {
        'teacher': teacher,
        'class_data': class_data,
    })


@login_required(login_url='attendance:login')
def take_attendance(request, class_name):
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        messages.error(request, 'No teacher profile found.')
        return redirect('attendance:home')

    if class_name not in teacher.get_class_list():
        messages.error(request, f'You are not assigned to class "{class_name}".')
        return redirect('attendance:teacher_dashboard')

    students = Student.objects.filter(class_name=class_name)
    today = __import__('datetime').date.today()

    context = {
        'class_name': class_name,
        'students': students,
        'today': today,
    }
    return render(request, 'attendance/take_attendance.html', context)


@login_required(login_url='attendance:login')
def process_attendance(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    class_name = request.POST.get('class_name')

    if request.POST.get('mark_remaining_absent'):
        student_ids_str = request.POST.get('student_ids', '')
        date_str = request.POST.get('date', '')
        if not student_ids_str or not date_str:
            return JsonResponse({'error': 'Missing student_ids or date'})
        from datetime import datetime
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'})
        student_ids = [sid.strip() for sid in student_ids_str.split(',') if sid.strip()]
        from .models import AttendanceRecord, Student
        students = Student.objects.filter(student_id__in=student_ids, class_name=class_name)
        for student in students:
            AttendanceRecord.objects.update_or_create(
                student=student,
                date=date_obj,
                defaults={'status': AttendanceRecord.ABSENT, 'note': 'Marked absent (not captured)'}
            )
        return JsonResponse({'success': True, 'marked_absent': students.count()})

    captured_image_data = request.POST.get('captured_image')

    if not class_name or not captured_image_data:
        return JsonResponse({'error': 'Missing class_name or captured_image'})

    try:
        format, imgstr = captured_image_data.split(';base64,')
        ext = format.split('/')[-1]
        image_bytes = base64.b64decode(imgstr)

        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{ext}') as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        from .recognize import recognize_and_mark_attendance
        result = recognize_and_mark_attendance(tmp_path, class_name)

        os.unlink(tmp_path)
        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({'error': str(e)})


def custom_admin(request):
    return render(request, 'attendance/custom_admin.html')


def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            captured_image = request.POST.get('captured_image')
            if captured_image:
                try:
                    format, imgstr = captured_image.split(';base64,')
                    ext = format.split('/')[-1]
                    image_file = ContentFile(
                        base64.b64decode(imgstr),
                        name=f'face_capture.{ext}'
                    )
                    student.face_image = image_file
                except Exception as e:
                    print("Camera Image Error:", e)
            student.save()
            messages.success(request, f'{student.first_name} {student.last_name} registered successfully.')
            return redirect('attendance:register_student')
    else:
        form = StudentRegistrationForm()

    return render(request, 'attendance/register_student.html', {'form': form})


def start_attendance(request):
    from .recognize import recognize_and_mark_attendance
    recognize_and_mark_attendance()
    return HttpResponse("Attendance Recognition Completed")


def attendance_daily(request):
    if request.method == 'POST':
        record_form = AttendanceRecordForm(request.POST)
        if record_form.is_valid():
            record, created = AttendanceRecord.objects.update_or_create(
                student=record_form.cleaned_data['student'],
                date=record_form.cleaned_data['date'],
                defaults={
                    'status': record_form.cleaned_data['status'],
                    'note': record_form.cleaned_data['note'],
                },
            )
            action = 'saved' if created else 'updated'
            messages.success(request, f'Attendance {action} for {record.student.student_id} on {record.date}.')
            return redirect('attendance:attendance_daily')
    else:
        record_form = AttendanceRecordForm()

    filter_form = AttendanceFilterForm(request.GET)
    records = AttendanceRecord.objects.select_related('student')

    if filter_form.is_valid():
        student_id = filter_form.cleaned_data.get('student_id')
        month = filter_form.cleaned_data.get('month')
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')

        if student_id:
            records = records.filter(student__student_id__icontains=student_id)
        if month:
            year, month_number = [int(part) for part in month.split('-')]
            records = records.filter(date__year=year, date__month=month_number)
        if start_date:
            records = records.filter(date__gte=start_date)
        if end_date:
            records = records.filter(date__lte=end_date)

    present_count = records.filter(status=AttendanceRecord.PRESENT).count()
    absent_count = records.filter(status=AttendanceRecord.ABSENT).count()
    total_count = records.count()

    return render(request, 'attendance/attendance_daily.html', {
        'record_form': record_form,
        'filter_form': filter_form,
        'records': records,
        'present_count': present_count,
        'absent_count': absent_count,
        'total_count': total_count,
    })
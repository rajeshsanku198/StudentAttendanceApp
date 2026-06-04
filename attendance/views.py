from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import AttendanceFilterForm, AttendanceRecordForm, StudentRegistrationForm
from .models import AttendanceRecord

import base64
from django.core.files.base import ContentFile


def home(request):
    return render(request, 'attendance/home.html')

def custom_admin(request):
    return render(request, 'attendance/custom_admin.html')

def register_student(request):
    if request.method == 'POST':

        form = StudentRegistrationForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            student = form.save(commit=False)

            captured_image = request.POST.get(
                'captured_image'
            )

            if captured_image:

                try:

                    format, imgstr = captured_image.split(
                        ';base64,'
                    )

                    ext = format.split('/')[-1]

                    image_file = ContentFile(
                        base64.b64decode(imgstr),
                        name=f'face_capture.{ext}'
                    )

                    student.face_image = image_file

                except Exception as e:
                    print("Camera Image Error:", e)

            student.save()

            messages.success(
                request,
                f'{student.first_name} '
                f'{student.last_name} '
                f'registered successfully.'
            )

            return redirect(
                'attendance:register_student'
            )

    else:

        form = StudentRegistrationForm()

    return render(
        request,
        'attendance/register_student.html',
        {
            'form': form
        }
    )

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

    return render(
        request,
        'attendance/attendance_daily.html',
        {
            'record_form': record_form,
            'filter_form': filter_form,
            'records': records,
            'present_count': present_count,
            'absent_count': absent_count,
            'total_count': total_count,
        },
    )

from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import StudentRegistrationForm


def home(request):
    return render(request, 'attendance/home.html')


def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save()
            messages.success(request, f'{student.first_name} {student.last_name} registered successfully.')
            return redirect('attendance:register_student')
    else:
        form = StudentRegistrationForm()

    return render(request, 'attendance/register_student.html', {'form': form})

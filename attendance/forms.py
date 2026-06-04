from django import forms
from django.utils import timezone

from .models import AttendanceRecord, Student


class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'first_name',
            'last_name',
            'student_id',
            'class_name',
            'email',
            'phone',
            'address',
            'face_image',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
            'student_id': forms.TextInput(attrs={'placeholder': 'Student ID'}),
            'class_name': forms.TextInput(attrs={'placeholder': 'Class or section'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email address'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone number'}),
            'address': forms.Textarea(attrs={'placeholder': 'Home address', 'rows': 4}),
        }


class AttendanceRecordForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['student', 'date', 'status', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'note': forms.TextInput(attrs={'placeholder': 'Optional note'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = timezone.localdate()
        self.fields['student'].queryset = Student.objects.order_by('student_id')
        self.fields['student'].empty_label = 'Select student'


class AttendanceFilterForm(forms.Form):
    student_id = forms.CharField(
        required=False,
        label='Student ID',
        widget=forms.TextInput(attrs={'placeholder': 'Search by ID'}),
    )
    month = forms.CharField(
        required=False,
        label='Month',
        widget=forms.TextInput(attrs={'type': 'month'}),
    )
    start_date = forms.DateField(
        required=False,
        label='From',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    end_date = forms.DateField(
        required=False,
        label='To',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    def clean_month(self):
        month = self.cleaned_data['month']
        if month:
            try:
                year, month_number = month.split('-')
                year = int(year)
                month_number = int(month_number)
            except ValueError as exc:
                raise forms.ValidationError('Enter a valid month.') from exc

            if month_number < 1 or month_number > 12:
                raise forms.ValidationError('Enter a valid month.')

            return f'{year:04d}-{month_number:02d}'

        return month

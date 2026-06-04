from django import forms

from .models import Student


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

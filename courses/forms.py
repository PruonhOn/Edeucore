from django import forms
from .models import Course, Enrollment, Announcement, Attendance
from accounts.models import User

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name','code','description','credits','department','instructor','max_students','status','semester','syllabus','schedule']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'code': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.Textarea(attrs={'class':'form-control','rows':3}),
            'credits': forms.NumberInput(attrs={'class':'form-control'}),
            'department': forms.Select(attrs={'class':'form-select'}),
            'instructor': forms.Select(attrs={'class':'form-select'}),
            'max_students': forms.NumberInput(attrs={'class':'form-control'}),
            'status': forms.Select(attrs={'class':'form-select'}),
            'semester': forms.Select(attrs={'class':'form-select'}),
            'syllabus': forms.Textarea(attrs={'class':'form-control','rows':4}),
            'schedule': forms.TextInput(attrs={'class':'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['instructor'].queryset = User.objects.filter(role__in=['sub_admin','super_admin'])
        if user and user.is_sub_admin:
            from accounts.models import Department
            self.fields['department'].queryset = Department.objects.filter(pk=user.department.pk) if user.department else Department.objects.none()

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student','course','status']

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title','content']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'content': forms.Textarea(attrs={'class':'form-control','rows':5}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student','date','status','notes']

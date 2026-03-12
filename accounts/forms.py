from django import forms
from .models import User, Department

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','email','phone','address','profile_picture','bio','date_of_birth','gender']
        widgets = {
            'first_name': forms.TextInput(attrs={'class':'form-control'}),
            'last_name': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'phone': forms.TextInput(attrs={'class':'form-control'}),
            'address': forms.Textarea(attrs={'class':'form-control','rows':3}),
            'bio': forms.Textarea(attrs={'class':'form-control','rows':3}),
            'date_of_birth': forms.DateInput(attrs={'class':'form-control','type':'date'}),
            'gender': forms.Select(attrs={'class':'form-select'}),
        }

class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))

    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','role','department','student_id','phone','gender','date_of_birth','password','confirm_password']
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control'}),
            'first_name': forms.TextInput(attrs={'class':'form-control'}),
            'last_name': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'role': forms.Select(attrs={'class':'form-select'}),
            'department': forms.Select(attrs={'class':'form-select'}),
            'student_id': forms.TextInput(attrs={'class':'form-control'}),
            'phone': forms.TextInput(attrs={'class':'form-control'}),
            'gender': forms.Select(attrs={'class':'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class':'form-control','type':'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get('password')
        cpw = cleaned_data.get('confirm_password')
        if pw and cpw and pw != cpw:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

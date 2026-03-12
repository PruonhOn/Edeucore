from django.contrib.auth.models import AbstractUser
from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('sub_admin', 'Sub Admin'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    student_id = models.CharField(max_length=20, blank=True, unique=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M','Male'),('F','Female'),('O','Other')], blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    @property
    def is_super_admin(self):
        return self.role == 'super_admin'

    @property
    def is_sub_admin(self):
        return self.role == 'sub_admin'

    @property
    def is_student(self):
        return self.role == 'student'

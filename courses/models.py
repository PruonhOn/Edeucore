from django.db import models
from accounts.models import User, Department

class AcademicYear(models.Model):
    year = models.CharField(max_length=9)  # e.g. 2024-2025
    is_current = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.year

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

class Semester(models.Model):
    SEMESTER_CHOICES = [('1','Semester 1'),('2','Semester 2'),('3','Summer')]
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    semester_number = models.CharField(max_length=1, choices=SEMESTER_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        unique_together = ['academic_year', 'semester_number']

    def __str__(self):
        return f"{self.academic_year} - Sem {self.semester_number}"

class Course(models.Model):
    STATUS_CHOICES = [('active','Active'),('inactive','Inactive'),('archived','Archived')]
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    credits = models.PositiveIntegerField(default=3)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='courses_taught')
    max_students = models.PositiveIntegerField(default=40)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='courses_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    syllabus = models.TextField(blank=True)
    schedule = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def enrolled_count(self):
        return self.enrollments.filter(status='enrolled').count()

class Enrollment(models.Model):
    STATUS_CHOICES = [('enrolled','Enrolled'),('dropped','Dropped'),('completed','Completed')]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='enrolled')

    class Meta:
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student} in {self.course}"

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='announcements', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_global = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Attendance(models.Model):
    STATUS_CHOICES = [('present','Present'),('absent','Absent'),('late','Late'),('excused','Excused')]
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ['student', 'course', 'date']

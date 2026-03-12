from django.db import models
from accounts.models import User
from courses.models import Course, Semester

class GradeCategory(models.Model):
    name = models.CharField(max_length=100)  # Quiz, Midterm, Final, Assignment
    weight = models.FloatField(default=0.0)  # percentage
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grade_categories')

    def __str__(self):
        return f"{self.name} ({self.weight}%) - {self.course.code}"

class Assessment(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(GradeCategory, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    max_score = models.FloatField(default=100.0)
    date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.course.code}"

class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='grades')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='grades')
    score = models.FloatField()
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='graded_assessments')
    graded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'assessment']

    @property
    def percentage(self):
        return (self.score / self.assessment.max_score) * 100

class SemesterResult(models.Model):
    GRADE_CHOICES = [
        ('A+','A+'),('A','A'),('A-','A-'),
        ('B+','B+'),('B','B'),('B-','B-'),
        ('C+','C+'),('C','C'),('C-','C-'),
        ('D','D'),('F','F'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='semester_results')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    total_score = models.FloatField(default=0.0)
    letter_grade = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    gpa_points = models.FloatField(default=0.0)
    remarks = models.TextField(blank=True)
    published = models.BooleanField(default=False)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='generated_results')
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'course', 'semester']

    def calculate_letter_grade(self):
        score = self.total_score
        if score >= 97: return 'A+', 4.0
        elif score >= 93: return 'A', 4.0
        elif score >= 90: return 'A-', 3.7
        elif score >= 87: return 'B+', 3.3
        elif score >= 83: return 'B', 3.0
        elif score >= 80: return 'B-', 2.7
        elif score >= 77: return 'C+', 2.3
        elif score >= 73: return 'C', 2.0
        elif score >= 70: return 'C-', 1.7
        elif score >= 60: return 'D', 1.0
        else: return 'F', 0.0

    def save(self, *args, **kwargs):
        grade, gpa = self.calculate_letter_grade()
        self.letter_grade = grade
        self.gpa_points = gpa
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.course.code} - {self.semester}"

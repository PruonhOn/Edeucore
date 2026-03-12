from django.contrib import admin
from .models import Grade, Assessment, GradeCategory, SemesterResult

admin.site.register(Grade)
admin.site.register(Assessment)
admin.site.register(GradeCategory)
admin.site.register(SemesterResult)

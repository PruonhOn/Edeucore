from django.contrib import admin
from .models import Course, Enrollment, AcademicYear, Semester, Announcement, Attendance

admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(AcademicYear)
admin.site.register(Semester)
admin.site.register(Announcement)
admin.site.register(Attendance)

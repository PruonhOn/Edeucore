from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('export/students/excel/', views.export_students_excel, name='export_students_excel'),
    path('export/students/csv/', views.export_students_csv, name='export_students_csv'),
    path('export/grades/excel/', views.export_grades_excel, name='export_grades_excel'),
    path('import/students/', views.import_students, name='import_students'),
    path('enrollment/', views.enrollment_report, name='enrollment_report'),
    path('gpa/', views.gpa_report, name='gpa_report'),
]

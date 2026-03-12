from django.urls import path
from . import views

urlpatterns = [
    path('', views.grade_list, name='grade_list'),
    path('course/<int:course_pk>/', views.course_grades, name='course_grades'),
    path('course/<int:course_pk>/assessment/add/', views.add_assessment, name='add_assessment'),
    path('course/<int:course_pk>/save/', views.save_grades, name='save_grades'),
    path('course/<int:course_pk>/generate/', views.generate_semester_results, name='generate_results'),
    path('course/<int:course_pk>/publish/', views.publish_results, name='publish_results'),
    path('course/<int:course_pk>/results/', views.semester_results, name='semester_results'),
]

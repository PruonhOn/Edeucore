from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('create/', views.create_course, name='create_course'),
    path('<int:pk>/', views.course_detail, name='course_detail'),
    path('<int:pk>/edit/', views.edit_course, name='edit_course'),
    path('<int:pk>/delete/', views.delete_course, name='delete_course'),
    path('<int:course_pk>/enroll/', views.enroll_student, name='enroll_student'),
    path('<int:course_pk>/announce/', views.post_announcement, name='post_announcement'),
    path('<int:course_pk>/attendance/', views.attendance_view, name='attendance_view'),
    path('<int:course_pk>/attendance/save/', views.save_attendance, name='save_attendance'),
]

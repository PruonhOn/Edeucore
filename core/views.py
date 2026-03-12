from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from accounts.models import User, Department
from courses.models import Course, Enrollment, Announcement
from grades.models import SemesterResult

@login_required
def dashboard(request):
    user = request.user
    context = {}
    
    if user.is_super_admin:
        context = {
            'total_students': User.objects.filter(role='student').count(),
            'total_courses': Course.objects.filter(status='active').count(),
            'total_departments': Department.objects.count(),
            'total_sub_admins': User.objects.filter(role='sub_admin').count(),
            'recent_courses': Course.objects.order_by('-created_at')[:5],
            'recent_announcements': Announcement.objects.order_by('-created_at')[:5],
            'department_stats': Department.objects.annotate(
                students=Count('user', filter=Q(user__role='student')),
                courses=Count('course', filter=Q(course__status='active'))
            )[:6],
        }
    elif user.is_sub_admin:
        dept_courses = Course.objects.filter(department=user.department)
        context = {
            'dept_courses': dept_courses.filter(status='active').count(),
            'dept_students': Enrollment.objects.filter(course__department=user.department, status='enrolled').values('student').distinct().count(),
            'recent_courses': dept_courses.order_by('-created_at')[:5],
            'announcements': Announcement.objects.filter(Q(course__department=user.department)|Q(is_global=True)).order_by('-created_at')[:5],
            'pending_grades': dept_courses.filter(semester_results__published=False).distinct().count() if dept_courses.exists() else 0,
        }
    else:  # student
        enrollments = Enrollment.objects.filter(student=user, status='enrolled').select_related('course','course__department')
        results = SemesterResult.objects.filter(student=user, published=True).select_related('course','semester')
        avg_gpa = sum(r.gpa_points for r in results) / results.count() if results.count() > 0 else 0
        context = {
            'enrollments': enrollments,
            'recent_results': results.order_by('-generated_at')[:5],
            'gpa': round(avg_gpa, 2),
            'total_credits': sum(e.course.credits for e in enrollments),
            'announcements': Announcement.objects.filter(
                Q(course__in=[e.course for e in enrollments])|Q(is_global=True)
            ).order_by('-created_at')[:5],
        }
    
    return render(request, 'core/dashboard.html', {'ctx': context})

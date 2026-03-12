from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Course, Enrollment, Semester, AcademicYear, Announcement, Attendance
from accounts.models import User, Department
from .forms import CourseForm, EnrollmentForm, AnnouncementForm, AttendanceForm

@login_required
def course_list(request):
    q = request.GET.get('q','')
    dept = request.GET.get('dept','')
    status = request.GET.get('status','')
    if request.user.is_super_admin:
        courses = Course.objects.all().select_related('department','instructor','semester')
    elif request.user.is_sub_admin:
        courses = Course.objects.filter(department=request.user.department).select_related('department','instructor','semester')
    else:
        courses = Course.objects.filter(enrollments__student=request.user, enrollments__status='enrolled').distinct()
    if q:
        courses = courses.filter(Q(name__icontains=q)|Q(code__icontains=q))
    if dept:
        courses = courses.filter(department_id=dept)
    if status:
        courses = courses.filter(status=status)
    departments = Department.objects.all()
    return render(request, 'courses/course_list.html', {'courses': courses, 'departments': departments, 'q': q, 'dept': dept, 'status': status})

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    enrollments = course.enrollments.filter(status='enrolled').select_related('student')
    announcements = course.announcements.all().order_by('-created_at')
    is_enrolled = False
    if request.user.is_student:
        is_enrolled = course.enrollments.filter(student=request.user, status='enrolled').exists()
    all_students = User.objects.filter(role='student').exclude(enrollments__course=course, enrollments__status='enrolled')
    return render(request, 'courses/course_detail.html', {'course': course, 'enrollments': enrollments, 'announcements': announcements, 'is_enrolled': is_enrolled, 'all_students': all_students})

@login_required
def create_course(request):
    if not (request.user.is_super_admin or request.user.is_sub_admin):
        messages.error(request, 'Access denied.')
        return redirect('course_list')
    form = CourseForm(request.POST or None, user=request.user)
    if request.method == 'POST' and form.is_valid():
        course = form.save(commit=False)
        course.created_by = request.user
        if request.user.is_sub_admin and not course.department:
            course.department = request.user.department
        course.save()
        messages.success(request, f'Course "{course.name}" created!')
        return redirect('course_detail', pk=course.pk)
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Create Course'})

@login_required
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if not (request.user.is_super_admin or (request.user.is_sub_admin and course.department == request.user.department)):
        messages.error(request, 'Access denied.')
        return redirect('course_list')
    form = CourseForm(request.POST or None, instance=course, user=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Course updated!')
        return redirect('course_detail', pk=course.pk)
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Edit Course', 'course': course})

@login_required
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if not (request.user.is_super_admin or (request.user.is_sub_admin and course.department == request.user.department)):
        messages.error(request, 'Access denied.')
        return redirect('course_list')
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted.')
        return redirect('course_list')
    return render(request, 'courses/confirm_delete.html', {'obj': course, 'type': 'course'})

@login_required
def enroll_student(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if request.method == 'POST':
        if request.user.is_student:
            if course.enrolled_count >= course.max_students:
                messages.error(request, 'Course is full.')
            else:
                Enrollment.objects.get_or_create(student=request.user, course=course, defaults={'status':'enrolled'})
                messages.success(request, f'Enrolled in {course.name}!')
        else:
            student_id = request.POST.get('student_id')
            if student_id:
                student = get_object_or_404(User, pk=student_id, role='student')
                Enrollment.objects.get_or_create(student=student, course=course, defaults={'status':'enrolled'})
                messages.success(request, f'{student.get_full_name()} enrolled!')
        return redirect('course_detail', pk=course_pk)

@login_required
def post_announcement(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if not (request.user.is_super_admin or request.user.is_sub_admin):
        messages.error(request, 'Access denied.')
        return redirect('course_detail', pk=course_pk)
    form = AnnouncementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ann = form.save(commit=False)
        ann.course = course
        ann.created_by = request.user
        ann.save()
        messages.success(request, 'Announcement posted!')
        return redirect('course_detail', pk=course_pk)
    return render(request, 'courses/announcement_form.html', {'form': form, 'course': course})

@login_required
def attendance_view(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if not (request.user.is_super_admin or (request.user.is_sub_admin and course.department == request.user.department)):
        messages.error(request, 'Access denied.')
        return redirect('course_detail', pk=course_pk)
    students = course.enrollments.filter(status='enrolled').select_related('student')
    return render(request, 'courses/attendance.html', {'course': course, 'students': students})

@login_required  
def save_attendance(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if request.method == 'POST':
        date = request.POST.get('date')
        students = course.enrollments.filter(status='enrolled').select_related('student')
        for enrollment in students:
            status = request.POST.get(f'status_{enrollment.student.pk}', 'absent')
            Attendance.objects.update_or_create(
                student=enrollment.student, course=course, date=date,
                defaults={'status': status}
            )
        messages.success(request, 'Attendance saved!')
    return redirect('attendance_view', course_pk=course_pk)

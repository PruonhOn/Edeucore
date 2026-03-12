from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Grade, Assessment, GradeCategory, SemesterResult
from courses.models import Course, Enrollment, Semester
from accounts.models import User

@login_required
def grade_list(request):
    if request.user.is_student:
        results = SemesterResult.objects.filter(student=request.user, published=True).select_related('course','semester')
        return render(request, 'grades/student_grades.html', {'results': results})
    
    if request.user.is_sub_admin:
        courses = Course.objects.filter(department=request.user.department)
    else:
        courses = Course.objects.all()
    return render(request, 'grades/grade_list.html', {'courses': courses})

@login_required
def course_grades(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if not (request.user.is_super_admin or (request.user.is_sub_admin and course.department == request.user.department)):
        messages.error(request, 'Access denied.')
        return redirect('grade_list')
    
    students = course.enrollments.filter(status='enrolled').select_related('student')
    assessments = course.assessments.all().select_related('category')
    categories = course.grade_categories.all()
    
    grade_matrix = {}
    for enrollment in students:
        grade_matrix[enrollment.student.pk] = {
            'student': enrollment.student,
            'grades': {}
        }
        for assessment in assessments:
            try:
                grade = Grade.objects.get(student=enrollment.student, assessment=assessment)
                grade_matrix[enrollment.student.pk]['grades'][assessment.pk] = grade.score
            except Grade.DoesNotExist:
                grade_matrix[enrollment.student.pk]['grades'][assessment.pk] = None
    
    return render(request, 'grades/course_grades.html', {
        'course': course, 'students': students, 'assessments': assessments,
        'categories': categories, 'grade_matrix': grade_matrix
    })

@login_required
def add_assessment(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if not (request.user.is_super_admin or (request.user.is_sub_admin and course.department == request.user.department)):
        messages.error(request, 'Access denied.')
        return redirect('course_grades', course_pk=course_pk)
    
    if request.method == 'POST':
        cat_name = request.POST.get('category_name')
        cat_weight = request.POST.get('category_weight', 0)
        cat_id = request.POST.get('category_id', '')
        
        if cat_id:
            category = get_object_or_404(GradeCategory, pk=cat_id, course=course)
        else:
            category, _ = GradeCategory.objects.get_or_create(name=cat_name, course=course, defaults={'weight': float(cat_weight)})
        
        Assessment.objects.create(
            name=request.POST.get('name'),
            category=category,
            course=course,
            max_score=float(request.POST.get('max_score', 100)),
            description=request.POST.get('description','')
        )
        messages.success(request, 'Assessment added!')
        return redirect('course_grades', course_pk=course_pk)
    
    categories = course.grade_categories.all()
    return render(request, 'grades/add_assessment.html', {'course': course, 'categories': categories})

@login_required
def save_grades(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if request.method == 'POST':
        assessments = course.assessments.all()
        students = course.enrollments.filter(status='enrolled').select_related('student')
        for enrollment in students:
            for assessment in assessments:
                score_key = f'score_{enrollment.student.pk}_{assessment.pk}'
                score = request.POST.get(score_key)
                if score is not None and score != '':
                    try:
                        score_val = float(score)
                        if score_val > assessment.max_score:
                            score_val = assessment.max_score
                        Grade.objects.update_or_create(
                            student=enrollment.student, assessment=assessment,
                            defaults={'score': score_val, 'graded_by': request.user}
                        )
                    except ValueError:
                        pass
        messages.success(request, 'Grades saved!')
    return redirect('course_grades', course_pk=course_pk)

@login_required
def generate_semester_results(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if not (request.user.is_super_admin or (request.user.is_sub_admin and course.department == request.user.department)):
        messages.error(request, 'Access denied.')
        return redirect('grade_list')
    
    if not course.semester:
        messages.error(request, 'Course has no semester assigned.')
        return redirect('course_grades', course_pk=course_pk)
    
    students = course.enrollments.filter(status='enrolled').select_related('student')
    categories = course.grade_categories.all()
    generated = 0
    
    for enrollment in students:
        total_weighted = 0.0
        total_weight = 0.0
        
        for category in categories:
            assessments = course.assessments.filter(category=category)
            cat_total = 0
            cat_max = 0
            for assessment in assessments:
                try:
                    grade = Grade.objects.get(student=enrollment.student, assessment=assessment)
                    cat_total += grade.score
                    cat_max += assessment.max_score
                except Grade.DoesNotExist:
                    cat_max += assessment.max_score
            
            if cat_max > 0:
                cat_pct = (cat_total / cat_max) * 100
                total_weighted += cat_pct * (category.weight / 100)
                total_weight += category.weight
        
        final_score = (total_weighted / total_weight * 100) if total_weight > 0 else total_weighted
        
        result, _ = SemesterResult.objects.update_or_create(
            student=enrollment.student, course=course, semester=course.semester,
            defaults={'total_score': round(final_score, 2), 'generated_by': request.user}
        )
        generated += 1
    
    messages.success(request, f'Generated results for {generated} students!')
    return redirect('course_grades', course_pk=course_pk)

@login_required
def publish_results(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    if request.method == 'POST':
        SemesterResult.objects.filter(course=course, semester=course.semester).update(published=True)
        messages.success(request, 'Results published to students!')
    return redirect('course_grades', course_pk=course_pk)

@login_required
def semester_results(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk)
    results = SemesterResult.objects.filter(course=course).select_related('student','semester')
    return render(request, 'grades/semester_results.html', {'course': course, 'results': results})

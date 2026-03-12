from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User, Department
from .forms import LoginForm, UserProfileForm, UserCreateForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def user_list(request):
    if not request.user.is_super_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    role = request.GET.get('role', '')
    dept = request.GET.get('dept', '')
    q = request.GET.get('q', '')
    users = User.objects.all().select_related('department')
    if role:
        users = users.filter(role=role)
    if dept:
        users = users.filter(department_id=dept)
    if q:
        users = users.filter(Q(first_name__icontains=q)|Q(last_name__icontains=q)|Q(username__icontains=q)|Q(email__icontains=q))
    departments = Department.objects.all()
    return render(request, 'accounts/user_list.html', {'users': users, 'departments': departments, 'role': role, 'dept': dept, 'q': q})

@login_required
def create_user(request):
    if not request.user.is_super_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    form = UserCreateForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        messages.success(request, f'User {user.get_full_name()} created successfully!')
        return redirect('user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Create User'})

@login_required
def edit_user(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if not request.user.is_super_admin and request.user != user_obj:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    form = UserProfileForm(request.POST or None, request.FILES or None, instance=user_obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User updated successfully!')
        return redirect('user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Edit User', 'user_obj': user_obj})

@login_required
def delete_user(request, pk):
    if not request.user.is_super_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user_obj.delete()
        messages.success(request, 'User deleted.')
        return redirect('user_list')
    return render(request, 'accounts/confirm_delete.html', {'obj': user_obj, 'type': 'user'})

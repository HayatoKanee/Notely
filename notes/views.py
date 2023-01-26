from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import SignUpForm, LogInForm, UserForm, ProfileForm
from .models import User
from django.contrib.auth.decorators import login_required
from .helpers import login_prohibited


@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('log_in')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


@login_prohibited
def log_in(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        next = request.POST.get('next') or ''
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                redirect_url = next or 'folders_tab'
                return redirect(redirect_url)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid.")
    else:
        next = request.GET.get('next') or ''
    form = LogInForm()
    return render(request, 'log_in.html', {'form': form, 'next': next})


@login_required
def log_out(request):
    logout(request)
    return redirect('home')


def home(request):
    return render(request, 'home.html')


@login_required
def folders_tab(request):
    return render(request, 'folders_tab.html')


@login_required
def calendar_tab(request):
    return render(request, 'calendar_tab.html')


@login_required
def profile_tab(request):
    if request.method == 'POST':
        user_form = UserForm(instance=request.user, data=request.POST)
        profile_form = ProfileForm(instance=request.user, data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.add_message(request, messages.SUCCESS, "Your profile is updated!")
            return redirect('profile_tab')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user)
    return render(request, 'profile_tab.html', {'user_form': user_form,
                                                'profile_form': profile_form})

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .util import EventCalendar
from .models import Event
from notely import settings
from .forms import SignUpForm, LogInForm, UserForm, ProfileForm, PasswordForm, FolderForm , EventForm
from .models import User, Folder
from django.contrib.auth.decorators import login_required
from .helpers import login_prohibited, check_perm
from django.contrib.auth.hashers import check_password
from guardian.shortcuts import get_objects_for_user
from django.utils import safestring


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


def log_out(request):
    logout(request)
    return redirect('home')


@login_prohibited
def home(request):
    return render(request, 'home.html')


@login_required
def folders_tab(request):
    user = request.user
    if request.method == "POST":
        form = FolderForm(request.POST)
        if form.is_valid():
            form.save(request.user)
    else:
        form = FolderForm()
    folders = get_objects_for_user(user, 'dg_view_folder', klass=Folder)
    folders = folders.filter(parent=None)

    return render(request, 'folders_tab.html',
                  {'folders': folders, 'form': form})


@login_required
@check_perm('view_folder', Folder)
def sub_folders_tab(request, folder_id):
    user = request.user
    folder = Folder.objects.get(id=folder_id)
    if request.method == "POST":
        form = FolderForm(request.POST)
        if form.is_valid():
            form.save(request.user, folder)
    else:
        form = FolderForm()
    return render(request, 'folders_tab.html',
                  {'folders': folder.sub_folders.all(), 'form': form ,'folder_id':folder_id})


@login_required
def calendar_tab(request):
    events = request.user.events.all()
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    cal = EventCalendar(currentYear,currentMonth,events)
    form = EventForm()
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            return redirect('calendar_tab')
        else:
            return redirect('calendar_tab')
    else:
        return render(request, 'calendar_tab.html' , {'calendar' : safestring.mark_safe(cal.formatmonth(withyear=True)) , 'form':form})



@login_required
def profile_tab(request):
    if request.method == 'POST':
        user_form = UserForm(instance=request.user, data=request.POST)
        profile_form = ProfileForm(instance=request.user.profile, data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.add_message(request, messages.SUCCESS, "Your profile is updated!")
            return redirect('profile_tab')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile_tab.html', {'user_form': user_form,
                                                'profile_form': profile_form})


@login_required
def password_tab(request):
    current_user = request.user
    if request.method == 'POST':
        form = PasswordForm(data=request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if check_password(password, current_user.password):
                new_password = form.cleaned_data.get('new_password')
                current_user.set_password(new_password)
                current_user.save()
                login(request, current_user, backend='django.contrib.auth.backends.ModelBackend')
                messages.add_message(request, messages.SUCCESS, "Password updated!")
                return redirect('folders_tab')
            else:
                messages.add_message(request, messages.ERROR, "Wrong Password!")
    form = PasswordForm()
    return render(request, 'password_tab.html', {'form': form})


def gravatar(request):
    return redirect("https://en.gravatar.com/")


@login_required
def page(request):
    return render(request, 'page.html')


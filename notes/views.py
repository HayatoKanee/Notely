from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import SignUpForm, LogInForm, UserForm, ProfileForm, PasswordForm, FolderForm, NotebookForm, EventForm, NotebookTagColorForm
from .models import User, Folder, Notebook, Page, Event
from django.contrib.auth.decorators import login_required
from .helpers import login_prohibited, check_perm
from django.contrib.auth.hashers import check_password
from guardian.shortcuts import get_objects_for_user, assign_perm
from .view_helper import sort_items_by_created_time, save_folder_notebook_forms
from datetime import datetime


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
        return save_folder_notebook_forms(request, user)
    else:
        folder_form = FolderForm()
        notebook_form = NotebookForm()
    folders = get_objects_for_user(user, 'dg_view_folder', klass=Folder)
    folders = folders.filter(parent=None)
    notebooks = get_objects_for_user(user, 'dg_view_notebook', klass=Notebook)
    notebooks = notebooks.filter(folder=None)
    items = sort_items_by_created_time(folders, notebooks)
    return render(request, 'folders_tab.html',
                  {'items': items, 'folder_form': folder_form,
                   'notebook_form': notebook_form})


@login_required
@check_perm('dg_view_folder', Folder)
def sub_folders_tab(request, folder_id):
    user = request.user
    folder = Folder.objects.get(id=folder_id)
    if request.method == "POST":
        return save_folder_notebook_forms(request, user, folder)
    else:
        folder_form = FolderForm()
        notebook_form = NotebookForm()
    folders = folder.sub_folders.all()
    notebooks = folder.notebooks.all()
    items = sort_items_by_created_time(folders, notebooks)
    return render(request, 'folders_tab.html',
                  {'items': items, 'folder_form': folder_form,
                   'notebook_form': notebook_form, 'folder': folder})


@login_required
def calendar_tab(request):
    events = request.user.events.all()
    form = EventForm()
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            messages.add_message(request, messages.SUCCESS, "Event Created!")
            return redirect('calendar_tab')
        else:
            messages.add_message(request, messages.ERROR, "Form is not valid. Please correct the errors and try again.")
    return render(request, 'calendar_tab.html',
                  {'form': form, 'events': events})


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
@check_perm('dg_view_page', Page)
def page(request, page_id):
    page = Page.objects.get(id=page_id)
    if request.method == 'POST':
        new_page = Page.objects.create(notebook=page.notebook)
        assign_perm('dg_view_page', request.user, new_page)
        assign_perm('dg_edit_page', request.user, new_page)
        assign_perm('dg_delete_page', request.user, new_page)
        return redirect('page', new_page.id)
    return render(request, 'page.html', {'page': page})


def save_page(request, page_id):
    if request.method == 'POST':
        data = request.POST.get('data')
        code = request.POST.get('code')
        page = Page.objects.get(id=page_id)
        notebook = page.notebook
        last_page = notebook.last_page
        last_page.last_page_of = None
        last_page.save()
        notebook.last_page = page
        notebook.save()
        page.drawing = data
        page.code = code
        page.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})


@login_required
@check_perm('dg_delete_folder', Folder)
def delete_folder(request, folder_id):
    user = request.user
    if request.method == 'GET':
        folder = Folder.objects.get(id=folder_id)
        folder.delete()
    return redirect('folders_tab')


@login_required
@check_perm('dg_delete_notebook', Notebook)
def delete_notebook(request, folder_id):
    user = request.user
    if request.method == 'GET':
        notebook = Notebook.objects.get(id=folder_id)
        notebook.delete()
    return redirect('folders_tab')


@login_required
def delete_event(request, event_id):
    event = Event.objects.get(id=event_id)
    event.delete()
    return redirect('calendar_tab')


@login_required
def update_event(request, event_id):
    if request.method == 'POST':
        start_time = request.POST.get('start')
        end_time = request.POST.get('end')
        event = Event.objects.get(id=event_id)
        event.start_time = datetime.fromisoformat(start_time[:-1])
        event.end_time = datetime.fromisoformat(end_time[:-1])
        event.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})

def notebook_tag_color(request):
    if request.method == 'POST':
        form = NotebookTagColorForm(request.POST)
        if form.is_valid():
            messages.add_message(request, messages.ERROR, "Wrong Color!")
    else:
        form = NotebookTagColorForm()
    return render(request, 'partials/notebook_sidebar.html', {'form': form})
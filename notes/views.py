import json
import base64
import os

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Q
from notifications.models import Notification
from oauthlib.oauth2 import AccessDeniedError

from .forms import SignUpForm, LogInForm, UserForm, ProfileForm, PasswordForm, FolderForm, NotebookForm, EventForm, \
    EventTagForm, PageTagForm, PageForm, ShareEventForm
from .models import User, Folder, Notebook, Page, Event, Editor, Reminder, Credential, PageTag, Template
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from .helpers import login_prohibited, check_perm
from django.contrib.auth.hashers import check_password
from guardian.shortcuts import get_objects_for_user, get_users_with_perms, assign_perm
from .view_helper import sort_items_by_created_time, save_folder_notebook_forms, get_or_create_event_from_google, \
    get_options, assign_perm_notebook, assign_perm_folder, share_obj, send_share_obj_noti, confirm_share_obj
from datetime import datetime
from django.utils import timezone
from google_auth_oauthlib.flow import Flow
from django.conf import settings
from django.core.mail import send_mail
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import sendgrid
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/contacts.readonly',
          'openid',
          'https://www.googleapis.com/auth/userinfo.profile']


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
                   'notebook_form': notebook_form,
                   'can_edit': True})


@login_required
@check_perm('dg_view_folder', Folder)
def sub_folders_tab(request, folder_id):
    user = request.user
    folder = Folder.objects.get(id=folder_id)
    can_edit = request.user.has_perm('dg_edit_folder', folder)
    if request.method == "POST":
        if not can_edit:
            raise PermissionDenied
        return save_folder_notebook_forms(request, user, folder)
    else:
        folder_form = FolderForm()
        notebook_form = NotebookForm()
    folders = get_objects_for_user(user, 'dg_view_folder', klass=Folder)
    folders = folders.filter(parent=folder)
    notebooks = get_objects_for_user(user, 'dg_view_notebook', klass=Notebook)
    notebooks = notebooks.filter(folder=folder)
    items = sort_items_by_created_time(folders, notebooks)

    return render(request, 'folders_tab.html',
                  {'items': items, 'folder_form': folder_form,
                   'notebook_form': notebook_form, 'folder': folder,
                   'can_edit': can_edit})


@login_required
def update_notifications(request):
    request.user.notifications.mark_all_as_read()
    return JsonResponse({'status': 'success'})


@login_required
@check_perm('dg_view_event', Event)
def calendar_tab(request):
    get_or_create_event_from_google(request)
    events = get_objects_for_user(request.user, 'dg_view_event', klass=Event)
    event_form = EventForm(request.user)
    tag_form = EventTagForm()
    shareEvent_form = ShareEventForm()
    tags = set()
    for event in events:
        # viewable_events = get_objects_for_user(request.user, 'dg_view_event', klass=Event).all()
        # users_with_perms = get_users_with_perms(event, only_with_perms_in=['dg_view_event'])
        # users_without_perms = User.objects.exclude(pk__in=users_with_perms).exclude(username='AnonymousUser')
        # can_edit = request.user.has_perm('dg_edit_event', event)

        for tag in event.tags.all():
            tags.add(tag)

    if request.method == "POST":
        if 'event_submit' in request.POST:
            event_form = EventForm(request.user, request.POST)
            if event_form.is_valid():

                page_data = event_form.cleaned_data['page']
                event = event_form.save()

                if page_data:
                    page_id = page_data.id
                    page = Page.objects.get(id=page_id)
                    event.save()  # Save the event after adding the page to the many-to-many relationship
                    event.pages.set([page])
                else:
                    event.save()  # Save the event without adding the page to the many-to-many relationship

                if int(event_form.cleaned_data['reminder']) > -1:
                    Reminder.objects.create(event=event, reminder_time=int(event_form.cleaned_data['reminder']))
                    messages.add_message(request, messages.SUCCESS, "Reminder Created!")
                messages.add_message(request, messages.SUCCESS, "Event Created!")
                return redirect('calendar_tab')

        if 'tag_submit' in request.POST:
            tag_form = EventTagForm(request.POST)
            if tag_form.is_valid():
                tag = tag_form.save(commit=False)
                tag.user = request.user
                tag.save()
                messages.add_message(request, messages.SUCCESS, "Tag Created!")
                return redirect('calendar_tab')

        if 'shareEvent_submit' in request.POST:
            shareEvent_form = ShareEventForm(request.POST)
            if shareEvent_form.is_valid():

                email = shareEvent_form.cleaned_data['email']
                message = shareEvent_form.cleaned_data['message']
                user = request.user.username

                event = shareEvent_form.cleaned_data['event']
                title = event.title
                description = event.description
                start_time = event.start_time
                end_time = event.end_time

                subject = f'You have been invited to the following event: {title}'

                html_content = f'<p>You have been invited to the following event: {title}\n</p> <p>by {user}\n</p> <p>Message from {user}: {message}\n</p> <p>Please see below event details:\n</p> <p>description: {description}\n</p> <p>start time: {start_time}\n</p> <p>end time: {end_time}</p>'

                mail = Mail(
                    from_email='winniethepooh.notely@gmail.com',
                    to_emails=email,
                    subject=subject,
                    html_content=html_content)

                try:
                    sg = SendGridAPIClient(
                        api_key=settings.EMAIL_HOST_PASSWORD
                    )
                    response = sg.send(mail)
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
                except Exception as ex:
                    print("a")
                messages.add_message(request, messages.SUCCESS, "Event Shared!")
                return redirect('calendar_tab')

    return render(request, 'calendar_tab.html', {'event_form': event_form, 'tag_form': tag_form, 'events': events,
                                                 'tags': tags, 'shareEvent_form': shareEvent_form})


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
    events = Event.objects.all()
    related_events = []
    for event in events:

        for related_page in event.pages.all():
            print(related_page)
            if related_page.id == page.id:
                related_events.append(event)
                print(event)
    print(related_events)
    page_tag_form = PageTagForm()
    tags = PageTag.objects.all()
    viewable_pages = get_objects_for_user(request.user, 'dg_view_page', klass=Page).filter(notebook=page.notebook)
    users_with_perms = get_users_with_perms(page, only_with_perms_in=['dg_view_page'])
    users_without_perms = User.objects.exclude(pk__in=users_with_perms).exclude(username='AnonymousUser')
    can_edit = request.user.has_perm('dg_edit_page', page)
    can_edit_notebook = request.user.has_perm('dg_edit_notebook', page.notebook)
    event_form = EventForm(request.user, initial={'page': page})
    tags = set()
    for event in events:

        for tag in event.tags.all():
            tags.add(tag)

    if request.method == 'POST':
        if 'event_submit' in request.POST:
            event_form = EventForm(request.user, request.POST)
            if event_form.is_valid():

                page_data = event_form.cleaned_data['page']
                event = event_form.save()

                if page_data:
                    page_id = page_data.id
                    page = Page.objects.get(id=page_id)
                    event.save()  # Save the event after adding the page to the many-to-many relationship
                    event.pages.set([page])
                else:
                    event.save()  # Save the event without adding the page to the many-to-many relationship

                if int(event_form.cleaned_data['reminder']) > -1:
                    Reminder.objects.create(event=event, reminder_time=int(event_form.cleaned_data['reminder']))
                    messages.add_message(request, messages.SUCCESS, "Reminder Created!")
                messages.add_message(request, messages.SUCCESS, "Event Created!")
                return redirect('page', page.id)
        if 'page_tag_submit' in request.POST:
            page_tag_form = PageTagForm(request.POST)
            if page_tag_form.is_valid():
                tag = page_tag_form.save(commit=False)
                tag.user = request.user
                tag.save()
                messages.add_message(request, messages.SUCCESS, "Tag Created!")
                return redirect('page', page.id)
        if 'add_page_submit' in request.POST:
            if not request.user.has_perm('dg_edit_notebook', page.notebook):
                raise PermissionDenied
            new_page = Page.objects.create(notebook=page.notebook)
            return redirect('page', new_page.id)
        if 'search_page_submit' in request.POST:
            new_page = Page.objects.get(id=page_id)
            return redirect('page', new_page.id)
    return render(request, 'page.html',
                  {'page': page, 'page_tag_form': page_tag_form, 'tags': tags, 'users': users_without_perms,
                   'viewable_pages': viewable_pages, 'can_edit': can_edit, 'can_edit_notebook': can_edit_notebook,
                   'events': related_events, 'templates': page.templates.all(),
                   'event_form': event_form})


@login_required
@check_perm('dg_edit_page', Page)
def save_page(request, page_id):
    if request.method == 'POST':
        canvas = request.POST.get('canvas')
        editors = json.loads(request.POST.get('editors'))
        thumbnail = request.POST.get('thumbnail')
        thumbnail_binary = base64.b64decode(thumbnail.split(',')[1])
        page = Page.objects.get(id=page_id)
        notebook = page.notebook
        last_page = notebook.last_page
        last_page.last_page_of = None
        last_page.save()
        notebook.last_page = page
        notebook.save()
        page.drawing = canvas
        page.editors.all().delete()
        page.thumbnail.save(f'{page.id}.jpeg', content=ContentFile(thumbnail_binary), save=True)
        page.save()
        for editor in editors:
            title = editor['title']
            code = editor['code']
            editor = Editor.objects.create(title=title, code=code, page=page)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})


@login_required
@check_perm('dg_delete_folder', Folder)
def delete_folder(request, folder_id):
    folder = Folder.objects.get(id=folder_id)
    folder.delete()
    return redirect('folders_tab')


@login_required
@check_perm('dg_delete_notebook', Notebook)
def delete_notebook(request, folder_id):
    notebook = Notebook.objects.get(id=folder_id)
    notebook.delete()
    return redirect('folders_tab')


@login_required
@check_perm('dg_delete_event', Event)
def delete_event(request, event_id):
    event = Event.objects.get(id=event_id)
    event.delete()
    return redirect('calendar_tab')


@login_required
@check_perm('dg_delete_page', Page)
def delete_page(request, page_id):
    page = Page.objects.get(id=page_id)
    notebook = page.notebook
    page.delete()
    notebook.refresh_from_db()
    return redirect('page', notebook.last_page.id)


@login_required
def event_detail(request, event_id):
    event = Event.objects.get(id=event_id)
    notebook_name = None
    page_number = None
    if event.pages.exists():
        notebook_name = event.pages.all()[0].notebook.notebook_name
        page_id = event.pages.all()[0].id
        page = Page.objects.get(id=page_id)
        print(event.pages.all(), event.pages.all()[0].id)
        page_number = page.get_page_number()

    if request.method == 'POST':
        if not request.user.has_perm('dg_edit_event', event):
            raise PermissionDenied

        form = EventForm(request.user, instance=event, data=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "event updated!")
            if int(form.cleaned_data['reminder']) > -1:
                Reminder.objects.create(event=event, reminder_time=int(form.cleaned_data['reminder']))
            return redirect('calendar_tab')

    else:
        form = EventForm(request.user, instance=event)
    html = render_to_string('partials/event_detail.html',
                            {'form': form, 'event': event,
                             'notebook_name': notebook_name,
                             'page_number': page_number
                             }, request=request)
    print(event.user.id)
    print(request.user.id)
    return JsonResponse({'html': html, 'event_user_id': event.user.id})


@login_required
def page_detail(request, page_id):
    page = Page.objects.get(id=page_id)
    if request.method == 'POST':
        form = PageForm(instance=page, data=request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, "page updated!")
            return redirect('page', page.id)
    form = PageForm(instance=page)
    html = render_to_string('partials/page_detail.html', {'form': form, 'page': page}, request=request)
    return JsonResponse({'html': html})


@login_required
@check_perm('dg_edit_event', Event)
def update_event(request, event_id):
    if request.method == 'POST':
        event = Event.objects.get(id=event_id)
        if not request.user.has_perm('dg_edit_event', event):
            raise PermissionDenied
        start_time = request.POST.get('start')
        end_time = request.POST.get('end')
        event.start_time = datetime.fromisoformat(start_time[:-1] + '+00:00')
        event.end_time = datetime.fromisoformat(end_time[:-1] + '+00:00')
        event.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'})


@login_required
def google_auth(request):
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CREDENTIALS_PATH,
        scopes=SCOPES, redirect_uri=request.build_absolute_uri('/google_auth_callback/')
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return redirect(authorization_url)


@login_required
def google_auth_callback(request):
    state = request.session.pop('google_auth_state', None)
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CREDENTIALS_PATH,
        scopes=SCOPES, redirect_uri=request.build_absolute_uri('/google_auth_callback/')
    )

    try:
        # Exchange authorization code for access token
        flow.fetch_token(authorization_response=request.build_absolute_uri(), state=state)
    except AccessDeniedError as e:
        messages.add_message(request, messages.ERROR, "Access denied. Please grant the requested permissions.")
    except Warning as e:
        messages.add_message(request, messages.ERROR, "Access denied. Please grant the requested permissions.")
        return redirect('calendar_tab')

    # Get the user's credentials and store them in the database
    credentials = flow.credentials.to_json()
    google_service = build('people', 'v1', credentials=flow.credentials)
    google_profile = google_service.people().get(resourceName='people/me', personFields='emailAddresses').execute()
    google_email = google_profile.get('emailAddresses', [])[0].get('value', '')
    Credential.objects.update_or_create(google_email=google_email,
                                        defaults={'google_cred': credentials, 'user': request.user})
    return redirect('calendar_tab')


@login_required
def share_page(request, page_id):
    try:
        page = Page.objects.get(id=page_id)
        return share_obj(request, page)
    except Page.DoesNotExist:
        return JsonResponse({'status': 'fail'})


@login_required
def get_options_notebook(request, notebook_id):
    try:
        notebook = Notebook.objects.get(id=notebook_id)
        return JsonResponse({
            'status': 'success',
            'options': get_options(notebook, 'dg_view_notebook')
        }, safe=False)
    except Notebook.DoesNotExist:
        return JsonResponse({'status': 'fail'})


@login_required
def get_options_folder(request, folder_id):
    try:
        folder = Folder.objects.get(id=folder_id)
        return JsonResponse({
            'status': 'success',
            'options': get_options(folder, 'dg_view_folder')
        }, safe=False)
    except Notebook.DoesNotExist:
        return JsonResponse({'status': 'fail'})


@login_required
def share_notebook(request, notebook_id):
    try:
        notebook = Notebook.objects.get(id=notebook_id)
        return share_obj(request, notebook)
    except Notebook.DoesNotExist:
        return JsonResponse({'status': 'fail'})


@login_required
def share_folder(request, folder_id):
    try:
        folder = Folder.objects.get(id=folder_id)
        return share_obj(request, folder)
    except Page.DoesNotExist:
        return JsonResponse({'status': 'fail'})


@login_required
def share_event(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
        if event.user != request.user:
            return JsonResponse({'status': 'fail'})
        selected_users = request.POST.getlist('selected_users[]')
        for email in selected_users:
            try:
                user = User.objects.get(email=email)
                assign_perm('dg_view_event', user, event)
                html = render_to_string('partials/share_event_internal.html', {'event': event}, request=request)
                return JsonResponse({'status': 'success', 'html': html})
            except:
                user = request.user.username

                title = event.title
                description = event.description
                start_time = event.start_time
                end_time = event.end_time

                subject = f'You have been invited to the following event: {title}'

                html_content = f'<p>You have been invited to the following event: {title}\n</p> <p>by {user}\n</p> <p>Please see below event details:\n</p> <p>description: {description}\n</p> <p>start time: {start_time}\n</p> <p>end time: {end_time}</p>'

                mail = Mail(
                    from_email='winniethepooh.notely@gmail.com',
                    to_emails=email,
                    subject=subject,
                    html_content=html_content)

                try:
                    sg = SendGridAPIClient(
                        api_key=settings.EMAIL_HOST_PASSWORD
                    )
                    response = sg.send(mail)
                except Exception as ex:
                    print("failed to share externally")
                messages.add_message(request, messages.SUCCESS, "Event Shared!")
                return JsonResponse({'status': 'fail'})
    except Event.DoesNotExist:
        return JsonResponse({'status': 'fail'})


@login_required
def get_options_event(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
        return JsonResponse({
            'status': 'success',
            'options': get_options(event, 'dg_view_event')
        }, safe=False)
    except Event.DoesNotExist:
        return JsonResponse({'status': 'fail'})


@login_required
@check_perm('dg_edit_page', Page)
def save_template(request, page_id):
    try:
        page = Page.objects.get(id=page_id)
        template_content = request.POST.get('template_content')
        Template.objects.create(page=page, content=template_content)
        return JsonResponse({'status': 'success'})
    except Page.DoesNotExist:
        return JsonResponse({'status': 'fail'})


@login_required
def confirm_share_page(request, page_id):
    return confirm_share_obj(request, page_id, Page)


@login_required
def confirm_share_notebook(request, notebook_id):
    return confirm_share_obj(request, notebook_id, Notebook)


@login_required
def confirm_share_folder(request, folder_id):
    return confirm_share_obj(request, folder_id, Folder)

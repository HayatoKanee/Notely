import datetime
import json

from django.http import JsonResponse
from guardian.shortcuts import get_users_with_perms, assign_perm
from notes.forms import FolderForm, NotebookForm
from django.contrib import messages
from django.shortcuts import redirect
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from notes.models import Credential, Event, Notebook, User


def save_folder_notebook_forms(request, user, folder=None):
    folder_form = FolderForm(request.POST)
    notebook_form = NotebookForm(request.POST)
    if folder_form.is_valid():
        folder_form.save(user, folder)
        messages.add_message(request, messages.SUCCESS, "Added a folder")
        if folder is None:
            return redirect('folders_tab')
        else:
            return redirect('sub_folders_tab', folder.id)
    if notebook_form.is_valid():
        notebook_form.save(user, folder)
        messages.add_message(request, messages.SUCCESS, "Added a notebook")
        if folder is None:
            return redirect('folders_tab')
        else:
            return redirect('sub_folders_tab', folder.id)


def sort_items_by_created_time(*args):
    items = []
    for arg in args:
        items += list(arg)
    return sorted(items, key=lambda x: x.created_at, reverse=True)


def get_or_create_event_from_google(request):
    credentials = request.user.creds.all()
    for credential in credentials:
        creds = Credentials.from_authorized_user_info(info=json.loads(credential.google_cred))
        # Create a service object to interact with the Google Calendar API
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API to get the upcoming events
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            if start.endswith('Z'):
                start = start[:-1] + '+00:00'
            if end.endswith('Z'):
                end = end[:-1] + '+00:00'
            start = datetime.datetime.fromisoformat(start)
            end = datetime.datetime.fromisoformat(end)
            title = event['summary']
            google_id = event.get('id')
            description = event.get('description', '')
            try:
                # Check if the event already exists in the GoogleEvent model
                google_event = Event.objects.get(google_id=google_id)
                google_event.title = title
                google_event.start_time = start
                google_event.end_time = end
                google_event.description = description
                google_event.save()
            except Event.DoesNotExist:
                google_event = Event.objects.create(
                    user=request.user,
                    google_id=google_id,
                    title=title,
                    description=description,
                    start_time=start,
                    end_time=end,
                    sync=True,
                    cred=credential
                )


def get_options(obj, perm_name):
    users_with_perms = get_users_with_perms(obj, only_with_perms_in=[perm_name])
    users_without_perms = User.objects.exclude(pk__in=users_with_perms).exclude(username='AnonymousUser')
    return [{'username': user.username, 'email': user.email, 'gravatar': user.profile.mini_gravatar()} for user in
            users_without_perms]


def assign_perm_notebook(user, notebook, can_edit=False):
    assign_perm('dg_view_notebook', user, notebook)
    assign_perm('dg_view_all_notebook', user, notebook)
    for page in notebook.pages.all():
        assign_perm('dg_view_page', user, page)
    if can_edit:
        assign_perm('dg_edit_notebook', user, notebook)
        assign_perm('dg_edit_all_notebook', user, notebook)
        for page in notebook.pages.all():
            assign_perm('dg_edit_page', user, page)
    folder = notebook.folder
    while folder:
        assign_perm('dg_view_folder', user, folder)
        folder = folder.parent


def assign_perm_folder(user, folder, can_edit=False):
    stack = [folder]
    while stack:
        current_folder = stack.pop()
        assign_perm('dg_view_folder', user, current_folder)
        assign_perm('dg_view_all_folder', user, current_folder)
        if can_edit:
            assign_perm('dg_edit_folder', user, current_folder)
            assign_perm('dg_edit_all_folder', user, current_folder)
        for notebook in current_folder.notebooks.all():
            assign_perm_notebook(user, notebook, can_edit)
        for sub_folder in current_folder.sub_folders.all():
            stack.append(sub_folder)
    parent = folder.parent
    while parent:
        assign_perm('dg_view_folder', user, parent)
        parent = parent.parent


def share_obj(request, obj):
    if obj.get_type() == 'Notebook':
        assign_perm_func = assign_perm_notebook
    elif obj.get_type() == 'Folder':
        assign_perm_func = assign_perm_folder
    if obj.user != request.user:
        return JsonResponse({'status': 'fail'})
    selected_users = request.POST.getlist('selected_users[]')
    edit_perm = request.POST.get('edit_perm')
    can_edit = edit_perm == "true"
    for email in selected_users:
        user = User.objects.get(email=email)
        assign_perm_func(user, obj, can_edit)
    return JsonResponse({'status': 'success'})

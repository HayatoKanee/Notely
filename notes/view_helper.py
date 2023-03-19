import datetime
import json

from django.core import signing
from django.http import JsonResponse
from google.auth.transport.requests import Request
from guardian.shortcuts import get_users_with_perms, assign_perm
from notifications.models import Notification
from notifications.signals import notify

from notes.forms import FolderForm, NotebookForm
from django.contrib import messages
from django.shortcuts import redirect
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from notes.models import Credential, Event, Notebook, User, Page, Folder


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
        print(credential.google_cred)
        if creds.expired:
            try:
                creds.refresh(Request())
                # Update the credentials in the database
                credential.google_cred = creds.to_json()
                credential.save()
            except Exception as e:
                messages.add_message(request, messages.ERROR, "Failed to refresh the credentials: {}".format(e))
                continue
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


def assign_perm_page(user, page, can_edit=False):
    assign_perm('dg_view_page', user, page)
    if can_edit:
        assign_perm('dg_edit_page', user, page)
    assign_perm('dg_view_notebook', user, page.notebook)
    folder = page.notebook.folder
    while folder:
        assign_perm('dg_view_folder', user, folder)
        folder = folder.parent


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


def confirm_share_obj(request, obj_id, obj_type):
    if request.method == 'POST':
        try:
            edit_perm = request.POST.get('edit_perm')
            obj = obj_type.objects.get(id=obj_id)

            notification = Notification.objects.filter(
                recipient=request.user,
                verb='Share',
            )
            if not notification.exists():
                return JsonResponse({'status': 'fail', 'message': 'No notification found'})
            assign_perm_functions = {
                Page: assign_perm_page,
                Notebook: assign_perm_notebook,
                Folder: assign_perm_folder
            }
            if obj_type in assign_perm_functions:
                assign_perm_functions[obj_type](request.user, obj, can_edit=edit_perm == "true")
            else:
                return JsonResponse({'status': 'fail', 'message': 'Invalid object type'})
            return JsonResponse({'status': 'success'})
        except obj_type.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Page not found'})
    else:
        return JsonResponse({'status': 'fail', 'message': 'Invalid request method'})


def share_obj(request, obj):
    if obj.get_owner() != request.user:
        return JsonResponse({'status': 'fail'})
    selected_users = request.POST.getlist('selected_users[]')
    edit_perm = request.POST.get('edit_perm')
    target = []
    for email in selected_users:
        user = User.objects.get(email=email)
        target.append(user)
    send_share_obj_noti(request.user, target, obj.id, obj.__class__.__name__, edit_perm == "true")
    return JsonResponse({'status': 'success'})


def send_share_obj_noti(sender, recipient, obj_id, obj_type, edit_perm):
    notify.send(
        sender=sender,
        recipient=recipient,
        verb='Share',
        description=f"{sender.username} share a {obj_type} to you",
        extra={
            'obj_id': obj_id,
            'obj_type': obj_type,
            'edit_perm': edit_perm,
        }
    )


def assign_perm_after_sign_up(obj_type, resolver_match, user):
    for obj_key, obj_class in obj_type.items():
        if f'{obj_key}_id' in resolver_match.kwargs:
            obj_id_en = resolver_match.kwargs[f'{obj_key}_id']
            obj_id = signing.loads(obj_id_en)
            obj = obj_class.objects.get(id=obj_id)
            assign_perm_functions = {
                Page: assign_perm_page,
                Notebook: assign_perm_notebook,
                Folder: assign_perm_folder
            }
            if obj_class in assign_perm_functions:
                assign_perm_functions[obj_class](user, obj)

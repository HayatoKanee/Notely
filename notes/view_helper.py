import datetime
import json

from notes.forms import FolderForm, NotebookForm
from django.contrib import messages
from django.shortcuts import redirect
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from notes.models import Credential


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


def get_google_events(request):
    try:
        credential = Credential.objects.get(user=request.user)
    except Credential.DoesNotExist:
        return None
    creds = Credentials.from_authorized_user_info(info=json.loads(credential.google_cred))
    # Create a service object to interact with the Google Calendar API
    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API to get the upcoming events
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    # Return the events as a JSON response
    event_list = []
    for event in events:
        google_id = event.get('id')
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        event_list.append({
            'google_id': google_id,
            'title': event['summary'],
            'start': start,
            'end': end
        })
    return event_list

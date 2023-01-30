from notes.forms import FolderForm, NotebookForm
from django.contrib import messages
from django.shortcuts import redirect


def save_folder_notebook_forms(request, user, folder=None):
    folder_form = FolderForm(request.POST)
    notebook_form = NotebookForm(request.POST)
    if folder_form.is_valid():
        folder_form.save(user, folder)
        messages.add_message(request, messages.SUCCESS, "Added a folder")
        return redirect('folders_tab' if folder is None else 'sub_folders_tab', folder.id if folder else None)
    if notebook_form.is_valid():
        notebook_form.save(user, folder)
        messages.add_message(request, messages.SUCCESS, "Added a notebook")
        return redirect('folders_tab' if folder is None else 'sub_folders_tab', folder.id if folder else None)


def sort_items_by_created_time(*args):
    items = []
    for arg in args:
        items += list(arg)
    return sorted(items, key=lambda x: x.created_at, reverse=True)

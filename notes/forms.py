from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from django import forms
from django.core.validators import RegexValidator
from django.utils.safestring import mark_safe

from .models import User, Profile, Folder, Notebook, Event, Tag, Page, EventTag , Reminder 
from guardian.shortcuts import assign_perm
from bootstrap_datepicker_plus.widgets import DateTimePickerInput,DatePickerInput,TimePickerInput
from colorfield.fields import ColorField
from django.forms import ModelChoiceField, widgets, ModelMultipleChoiceField
from django.utils.html import format_html
from django.forms.widgets import Select, SelectMultiple


class LogInForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'password']


class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8}.*$',
            message='Password must contain a uppercase character, a lowercase'
                    ' character and a number and at least 8 characters long'
        )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self):
        super().save(commit=False)
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )
        return user


class DateInput(forms.DateInput):
    input_type = 'date'


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['dob', 'address']
        widgets = {
            'address': forms.Textarea(),
            'dob': DateInput
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class PasswordForm(forms.Form):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8}.*$',
            message='Password must contain a uppercase character, a lowercase'
                    ' character and a number and at least 8 characters long'
        )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['folder_name']

    def save(self, user, parent=None):
        super().save(commit=False)
        folder = Folder.objects.create(
            user=user,
            parent=parent,
            folder_name=self.cleaned_data.get('folder_name'),
        )
        assign_perm('dg_view_folder', user, folder)
        assign_perm('dg_edit_folder', user, folder)
        assign_perm('dg_delete_folder', user, folder)
        return folder


class TagImageChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return mark_safe('{} {}'.format('&#x25CF', obj.title))


class TagSelectWidget(SelectMultiple):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        try:
            tag = EventTag.objects.get(title=label.replace('&#x25CF ', ''))
            option['attrs']['style'] = f'color: {tag.color}'
        except EventTag.DoesNotExist:
            pass
        return option


class EventForm(forms.ModelForm):
    tag = TagImageChoiceField(queryset=None, label="tags", required=False)
    page = forms.ModelChoiceField(queryset=Page.objects.all(), required=False)
    reminder = forms.ChoiceField(choices=Reminder.reminder_choice , required= False)
    class Meta:
        model = Event
        fields = ['title', 'description', 'start_time', 'end_time']
        widgets = {
            "start_time": DateTimePickerInput(attrs={"class": "form-control"}),
            "end_time": DateTimePickerInput(attrs={"class": "form-control"}),

        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['tag'].widget = TagSelectWidget()
        self.fields['tag'].queryset = user.event_tags.all()

    def clean(self):
        super().clean()
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')
        if end_time < start_time:
            self.add_error('end_time', 'End Time cannot be less that Start Time')

    def save(self):
        event = super().save(commit=False)
        event.user = self.user
        event.save()
        if self.cleaned_data.get('tag'):
            event.tags.set(self.cleaned_data['tag'])
        event.save()
        return event


class EventTagForm(forms.ModelForm):
    class Meta:
        model = EventTag
        fields = ['title', 'color']


class PageTagForm(forms.ModelForm):
    class Meta:
        model = EventTag
        fields = ['title', 'color']


class NotebookForm(forms.ModelForm):
    class Meta:
        model = Notebook
        fields = ['notebook_name']

    def save(self, user, folder=None):
        super().save(commit=False)
        notebook = Notebook.objects.create(
            user=user,
            folder=folder,
            notebook_name=self.cleaned_data.get('notebook_name'),
        )
        assign_perm('dg_view_notebook', user, notebook)
        assign_perm('dg_edit_notebook', user, notebook)
        assign_perm('dg_delete_notebook', user, notebook)
        return notebook

class reminderForm(forms.ModelForm):
    event = forms.ModelChoiceField(queryset=Event.objects.all(), required=False)
    class Meta:
        model = Reminder 
        fields = ['event','reminder_time']


    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['event'].queryset = user.events.all()
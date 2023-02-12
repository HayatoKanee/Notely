from django import forms
from django.core.validators import RegexValidator
from .models import User, Profile, Folder, Event, Tag, Notebook
from guardian.shortcuts import assign_perm
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from colorfield.fields import ColorField
from django.forms import ModelChoiceField, widgets
from django.utils.html import format_html
from django.forms.widgets import Select

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


from django.utils.safestring import mark_safe

class TagImageChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        dot_html = '<span style="color:{}">&#x25CF;</span>'.format(obj.color)
        return mark_safe('{} {}'.format(dot_html, obj.title))

class EventForm(forms.ModelForm):
    tag = TagImageChoiceField(queryset=None, empty_label="--Select tag--", label="Tag")  
    class Meta:     
        model = Event
        fields = ['title', 'description', 'start_time', 'end_time' , 'tag']
        widgets = {
            "start_time": DateTimePickerInput(),
            "end_time": DateTimePickerInput(),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tag'].queryset = Tag.objects.filter(user=user)

    def clean(self):
        super().clean()
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')
        if end_time < start_time:
            self.add_error('end_time', 'End Time cannot be less that Start Time')


    
    
class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
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

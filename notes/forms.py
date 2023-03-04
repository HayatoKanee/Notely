from django import forms
from django.core.validators import RegexValidator
from django.utils.safestring import mark_safe
from .models import User, Profile, Folder, Notebook, Page, EventTag, Reminder, Event, PageTag
from guardian.shortcuts import assign_perm
from bootstrap_datepicker_plus.widgets import DateTimePickerInput
from django.forms import ModelMultipleChoiceField
from django.forms.widgets import SelectMultiple


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
        return folder


class TagImageChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return mark_safe('{} {} {} '.format(obj.id, '&#x25CF', obj.title))


class TagSelectWidget(SelectMultiple):
    tag_model = None

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        try:
            tag_id = label.split('&#x25CF')[0]
            title = label.split('&#x25CF')[1]
            tag = self.tag_model.objects.get(id=tag_id)
            option['attrs']['style'] = f'color: {tag.color}'
            option['label'] = mark_safe('{} {} '.format('&#x25CF', title))
        except self.tag_model.DoesNotExist:
            pass
        return option


class PageTagSelectWidget(TagSelectWidget):
    tag_model = PageTag


class EventTagSelectWidget(TagSelectWidget):
    tag_model = EventTag


class EventForm(forms.ModelForm):
    tag = TagImageChoiceField(queryset=None, label="tags", required=False)
    # page = forms.ModelMultipleChoiceField(
    #     queryset=Page.objects.all(),
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False,
    # )
    page = forms.ModelChoiceField(queryset=Page.objects.all(), required=False)
    reminder = forms.ChoiceField(choices=Reminder.reminder_choice, required=False, initial="No reminder")
    sync = forms.BooleanField(required=False)

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
        self.fields['tag'].widget = EventTagSelectWidget()
        self.fields['tag'].queryset = user.event_tags.all()



        notebook_choices = []
        notebooks = Notebook.objects.filter(user=user)
        for notebook in notebooks:
            for i, page in enumerate(notebook.pages.all()):
                notebook_choices.append((page.id, f"{notebook.notebook_name}: {i+1}"))

        self.fields['page'].choices = notebook_choices

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
        if self.cleaned_data.get('page'):
            page_id = self.cleaned_data['page'].id
            page = Page.objects.get(id=page_id)
            event.save()  # Save the event after adding the page to the many-to-many relationship
            event.pages.set([page])
        if self.cleaned_data.get('sync'):
            event.sync = True
        self.save_m2m()
        event.save()
        return event


class EventTagForm(forms.ModelForm):
    class Meta:
        model = EventTag
        fields = ['title', 'color']


class PageTagForm(forms.ModelForm):  # The form for the tag.
    class Meta:
        model = PageTag
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
        return notebook


class ReminderForm(forms.ModelForm):
    event = forms.ModelChoiceField(queryset=Event.objects.all(), required=False)

    class Meta:
        model = Reminder
        fields = ['event', 'reminder_time']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['event'].queryset = user.events.all()


class PageForm(forms.ModelForm):  # The form for linking the tag and the page.
    tag = TagImageChoiceField(queryset=None, label="tags", required=False)

    class Meta:
        model = Page
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tag'].widget = PageTagSelectWidget()
        self.fields['tag'].queryset = PageTag.objects.all()

    def save(self):
        page = super().save(commit=False)
        if self.cleaned_data.get('tag'):
            page.tags.set(self.cleaned_data['tag'])
        page.save()
        return page


class ShareEventForm(forms.Form):
    event = forms.ModelChoiceField(queryset=Event.objects.all(), required=False)
    email = forms.EmailField(required=False)
    message = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['event'].choices = [(event.id, f"{event.title}") for event in Event.objects.all()]

    

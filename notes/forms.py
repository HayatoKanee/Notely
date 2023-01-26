from django import forms
from django.core.validators import RegexValidator
from .models import User

class LogInForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'password']


class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'new_password', 'password_confirmation']

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[
            RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase character and a number'
            ),
        ]
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
                self.cleaned_data.get('username'),
                first_name = self.cleaned_data.get('email'),
                password= self.cleaned_data.get('new_password'),
            )
        return user
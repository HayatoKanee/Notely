import datetime

from django.conf import settings
from django.shortcuts import redirect
from django.core.exceptions import ValidationError

def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)

    return modified_view_function


def calculate_age(dob):
    today = datetime.date.today()
    age = today.year - dob.year
    if (dob.month, dob.day) >= (today.month, today.day):
        age += 1
    return age


def validate_date(date):
    if date > datetime.date.today():
        raise ValidationError("The date of birth should not be in the future!")

import datetime

from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import ValidationError, PermissionDenied
from functools import wraps


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


def check_perm(perm, obj_type):
    def decorator(view_function):
        @wraps(view_function)
        def modified_view_function(request, *args, **kwargs):
            for arg in args:
                obj = get_object_or_404(obj_type, id=arg)
                if not request.user.has_perm(perm, obj):
                    raise PermissionDenied
            result = view_function(request, *args, **kwargs)
            return result

        return modified_view_function

    return decorator



from django.contrib import admin
from .models import Reminder,Event,Tag

# Register your models here.
@admin.register(Reminder )
class ReminderAdmin(admin.ModelAdmin):
    pass
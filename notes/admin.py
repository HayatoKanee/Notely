from django.contrib import admin
from .models import Reminder,Event,Page, Notebook

# Register your models here.
@admin.register(Reminder )
class ReminderAdmin(admin.ModelAdmin):
    pass

@admin.register(Event )
class EventAdmin(admin.ModelAdmin):
    pass

@admin.register(Notebook )
class NotebookAdmin(admin.ModelAdmin):
    pass

@admin.register(Page )
class PageAdmin(admin.ModelAdmin):
    pass
"""notely URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from notes import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    path('log_in/', views.log_in, name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('folders_tab/', views.folders_tab, name='folders_tab'),
    path('folders_tab/<folder_id>', views.sub_folders_tab, name='sub_folders_tab'),
    path('delete_folder_tab/<folder_id>', views.delete_folder, name='delete_folder_tab'),
    path('delete_notebook_tab/<folder_id>', views.delete_notebook, name='delete_notebook_tab'),
    path('calendar_tab/', views.calendar_tab, name='calendar_tab'),
    # path('page/<page_id>', views.notebook_tag_color, name='notebook_sidebar'),
    path('profile_tab/', views.profile_tab, name='profile_tab'),
    path('password_tab/', views.password_tab, name='password_tab'),
    path('gravatar/', views.gravatar, name='gravatar'),
    path('page/<page_id>', views.page, name='page'),
    path('save_page/<page_id>', views.save_page, name='save_page'),
    path('delete_event/<event_id>', views.delete_event, name='delete_event'),
    path('update_event/<event_id>', views.update_event, name='update_event'),
    path('event_detail/<event_id>', views.event_detail, name='event_detail'),
]

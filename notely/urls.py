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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from notes import views
from django.urls import path, include, re_path
import notifications.urls

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
    path('profile_tab/', views.profile_tab, name='profile_tab'),
    path('password_tab/', views.password_tab, name='password_tab'),
    path('gravatar/', views.gravatar, name='gravatar'),
    path('page/<page_id>', views.page, name='page'),
    path('save_page/<page_id>', views.save_page, name='save_page'),
    path('delete_event/<event_id>', views.delete_event, name='delete_event'),
    path('update_event/<event_id>', views.update_event, name='update_event'),
    path('event_detail/<event_id>', views.event_detail, name='event_detail'),
    path('google_auth/', views.google_auth, name='google_auth'),
    path('google_auth_callback/', views.google_auth_callback, name='google_auth_callback'),
    path('page_detail/<page_id>', views.page_detail, name='page_detail'),
    path('delete_page/<page_id>', views.delete_page, name='delete_page'),
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    re_path(r'^update_notifications/$', views.update_notifications, name='update_notifications'),
    path('share_page/<page_id>', views.share_page, name='share_page'),
    path('get_options_notebook/<notebook_id>', views.get_options_notebook, name='get_options_notebook'),
    path('get_options_folder/<folder_id>', views.get_options_folder, name='get_options_folder'),
    path('share_folder/<folder_id>', views.share_folder, name='share_folder'),
    path('share_notebook/<notebook_id>', views.share_notebook, name='share_notebook'),
    path('share_event/<event_id>/', views.share_event, name='share_event'),
    path('get_options_event/<event_id>', views.get_options_event, name='get_options_event'),
    path('save_template/<page_id>', views.save_template, name='save_template'),
    path('confirm_share_page/<page_id>', views.confirm_share_page, name='confirm_share_page'),
    path('confirm_share_notebook/<notebook_id>', views.confirm_share_notebook, name='confirm_share_notebook'),
    path('confirm_share_folder/<folder_id>', views.confirm_share_folder, name='confirm_share_folder'),
    path('share_page_ex/<page_id>', views.share_page_ex, name='share_page_ex')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

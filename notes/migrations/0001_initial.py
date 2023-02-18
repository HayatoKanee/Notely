# Generated by Django 4.1.5 on 2023-02-18 16:43

import colorfield.fields
from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import notes.helpers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=30, unique=True, validators=[django.core.validators.RegexValidator(message='Username must contain at least three alphanumericals and only alphanumericals', regex='^\\w{3}\\w*$')])),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(default='')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('routine', models.CharField(blank=True, choices=[('0', 'No Repeat'), ('1', 'every Day'), ('2', 'every Week'), ('3', 'every 2 Weeks'), ('4', 'every Month'), ('5', 'every Year'), ('Custom', 'Custom')], max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('folder_name', models.CharField(max_length=10)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_folders', to='notes.folder')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='folders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('dg_view_folder', 'can view folder'), ('dg_edit_folder', 'can edit folder'), ('dg_delete_folder', 'can delete folder')],
            },
        ),
        migrations.CreateModel(
            name='Notebook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notebook_name', models.CharField(max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('folder', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notebooks', to='notes.folder')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notebooks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('dg_view_notebook', 'can view notebook'), ('dg_edit_notebook', 'can edit notebook'), ('dg_delete_notebook', 'can delete notebook')],
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drawing', models.TextField(blank=True)),
                ('last_page_of', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='last_page', to='notes.notebook')),
                ('notebook', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='notes.notebook')),
            ],
            options={
                'permissions': [('dg_view_page', 'can view page'), ('dg_edit_page', 'can edit page'), ('dg_delete_page', 'can delete page')],
            },
        ),
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reminder_time', models.CharField(blank=True, choices=[('0', 'When event start'), ('1', '5 minutes before'), ('4', '10 minutes before'), ('2', '15 minutes before'), ('3', '30 minutes before'), ('4', '1  hour before'), ('5', '2  hours before'), ('6', '1  day before'), ('7', '2  days before'), ('8', '1  week before')], max_length=10)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reminders', to='notes.event')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(limit_value=0, message='Age cannot be a negative number'), django.core.validators.MaxValueValidator(limit_value=180, message='Age is too high')])),
                ('dob', models.DateField(blank=True, null=True, validators=[notes.helpers.validate_date])),
                ('address', models.CharField(blank=True, max_length=200, null=True, validators=[django.core.validators.RegexValidator(message='Address must only contain alphanuericals, spaces or commas', regex='^[\\w|,|\\s]*$')])),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PageTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30, unique=True)),
                ('image', models.ImageField(upload_to='images')),
                ('color', colorfield.fields.ColorField(blank=True, default='', image_field='image', max_length=18, samples=[('#000000', 'black'), ('#0000FF', 'Blue'), ('#C12FFF', 'Purple'), ('#34eb67', 'green'), ('#FF5B09', 'orange'), ('#FC1501', 'red'), ('#FFFF00', 'Yellow'), ('#FFA3EE', 'Pink')])),
                ('pages', models.ManyToManyField(blank=True, related_name='tags', to='notes.page')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='page_tags', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EventTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30, unique=True)),
                ('image', models.ImageField(upload_to='images')),
                ('color', colorfield.fields.ColorField(blank=True, default='', image_field='image', max_length=18, samples=[('#000000', 'black'), ('#0000FF', 'Blue'), ('#C12FFF', 'Purple'), ('#34eb67', 'green'), ('#FF5B09', 'orange'), ('#FC1501', 'red'), ('#FFFF00', 'Yellow'), ('#FFA3EE', 'Pink')])),
                ('events', models.ManyToManyField(blank=True, related_name='tags', to='notes.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_tags', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Editor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=10)),
                ('code', models.TextField(blank=True)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='editors', to='notes.page')),
            ],
        ),
    ]

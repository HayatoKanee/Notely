# Generated by Django 4.1.6 on 2023-02-15 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagetag',
            name='pages',
            field=models.ManyToManyField(blank=True, related_name='notebooks_tags', to='notes.page'),
        ),
    ]

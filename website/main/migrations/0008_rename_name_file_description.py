# Generated by Django 5.0.1 on 2024-01-24 16:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_file'),
    ]

    operations = [
        migrations.RenameField(
            model_name='file',
            old_name='name',
            new_name='description',
        ),
    ]

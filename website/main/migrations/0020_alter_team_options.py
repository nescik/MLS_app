# Generated by Django 5.0.1 on 2024-02-19 23:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_alter_team_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='team',
            options={'permissions': [('add_new_member', 'Can add new team memeber'), ('delete_member', 'Can delete team memeber')]},
        ),
    ]

# Generated by Django 5.0.1 on 2024-01-22 18:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_profile_age_profile_bio_profile_country_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('founder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_founder', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(related_name='team_member', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

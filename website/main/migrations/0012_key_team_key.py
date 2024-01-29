# Generated by Django 5.0.1 on 2024-01-29 13:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_alter_file_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=44)),
            ],
        ),
        migrations.AddField(
            model_name='team',
            name='key',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='team_key', to='main.key'),
            preserve_default=False,
        ),
    ]

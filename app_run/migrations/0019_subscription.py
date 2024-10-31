# Generated by Django 5.0.2 on 2024-10-30 22:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_run', '0018_alter_position_distance_alter_position_speed_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('athlete', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coaches', to=settings.AUTH_USER_MODEL)),
                ('coach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='athletes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('coach', 'athlete')},
            },
        ),
    ]
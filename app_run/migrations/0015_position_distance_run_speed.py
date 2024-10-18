# Generated by Django 5.0.2 on 2024-10-18 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_run', '0014_remove_run_speed_position_speed'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='distance',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='run',
            name='speed',
            field=models.FloatField(default=0),
        ),
    ]

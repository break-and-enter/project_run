# Generated by Django 5.0.2 on 2024-10-18 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_run', '0016_alter_position_distance_alter_position_speed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='run',
            name='distance',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]

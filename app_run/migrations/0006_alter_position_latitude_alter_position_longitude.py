# Generated by Django 5.0.2 on 2024-09-21 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_run', '0005_alter_position_latitude_alter_position_longitude'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='latitude',
            field=models.DecimalField(decimal_places=4, max_digits=7),
        ),
        migrations.AlterField(
            model_name='position',
            name='longitude',
            field=models.DecimalField(decimal_places=4, max_digits=8),
        ),
    ]

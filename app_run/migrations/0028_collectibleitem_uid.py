# Generated by Django 5.0.2 on 2024-12-05 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_run', '0027_collectibleitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectibleitem',
            name='uid',
            field=models.CharField(default='', max_length=200),
        ),
    ]

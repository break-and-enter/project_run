from django.db import models
from django.contrib.auth.models import User


STATUS_CHOICES = [
    ('init', 'Старт забега'),
    ('in_progress', 'Забег в процессе'),
    ('finished', 'Забег окончен'),
]

class Run(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    comment = models.TextField()
    athlete = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='init')
    distance = models.FloatField(default=0)
    run_time_seconds = models.PositiveIntegerField(default=0)

class Position(models.Model):
    latitude = models.DecimalField(decimal_places=4, max_digits=7)
    longitude = models.DecimalField(decimal_places=4, max_digits=8)
    run = models.ForeignKey(Run, on_delete=models.CASCADE)


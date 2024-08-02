from django.db import models

class Babaika(models.Model):
    name = models.CharField(max_length=50)

class Auto(models.Model):
    m = models.IntegerField(default=0)

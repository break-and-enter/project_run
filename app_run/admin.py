from django.contrib import admin
from app_run.models import Run, Position, Subscription, Challenge, AthleteInfo, CollectibleItem

admin.site.register(Run)
admin.site.register(Position)
admin.site.register(Subscription)
admin.site.register(Challenge)
admin.site.register(AthleteInfo)
admin.site.register(CollectibleItem)


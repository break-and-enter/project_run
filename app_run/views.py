from rest_framework import viewsets
from .models import Run
from .serializers import RunSerializer


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all()
    serializer_class = RunSerializer
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Run
from .serializers import RunSerializer


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all()
    serializer_class = RunSerializer


class StatusStartView(APIView):
    def post(self, request, run_id):
        run = Run.objects.get(id=run_id)
        run.status = 'in_progress'
        run.save()
        return Response({'message': 'Все ништяк'}, status=status.HTTP_200_OK)
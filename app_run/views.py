from rest_framework import viewsets, status
from rest_framework.decorators import api_view
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
        if run.status == 'init':
            run.status = 'in_progress'
            run.save()
            return Response({'message': 'Все ништяк'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Ты чо! Этот забег стартовать нельзя, он уже стартовал'},
                            status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def status_stop_view(request, run_id):
    run = Run.objects.get(id=run_id)
    if run.status == 'in_progress':
        run.status = 'finished'
        run.save()
        return Response({'message': 'Все ништяк'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Ты чо! Этот забег финишировать нельзя, он еще не стартовал или уже завершен'},
                        status=status.HTTP_400_BAD_REQUEST)
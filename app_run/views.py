from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Run, Position
from .serializers import RunSerializer


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all()
    serializer_class = RunSerializer


class StatusStartView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        if run.status == 'init':
            run.status = 'in_progress'
            run.save()
            return Response({'message': 'Все ништяк'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Ты чо! Этот забег стартовать нельзя, он уже стартовал'},
                            status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def status_stop_view(request, run_id):
    run = get_object_or_404(Run,id=run_id)
    if run.status == 'in_progress':
        run.status = 'finished'
        run.save()
        return Response({'message': 'Все ништяк'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'Ты чо! Этот забег финишировать нельзя, он еще не стартовал или уже завершен'},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def company_details(request):
    return Response({'company_name': 'Космическая Картошка',
                     'slogan':'Картофельное Пюре - путь к звездам!',
                     'contacts': 'Город Задунайск, улица Картофельная дом 16'}, status=status.HTTP_200_OK)


# @api_view(['GET', 'POST'])
# def position_view(request, run_id):
#     if request.method == 'GET':
#         position = Position.objects.get(id=run_id)
#         return Response({'latitude': position.latitude, 'longitude': position.longitude})
#     if request.method == 'POST':
#         latitude = request.POST.get('latitude')
#         longitude = request.POST.get('longitude')
#         position = Position.objects.create(run=run_id, latitude = latitude, longitude = longitude)
#         return Response({'message': 'Position created'})

class PositionView(APIView):
    def post(self, request):
        run_id = request.POST.get('run_id')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        run = get_object_or_404(Run,id=run_id)
        if run.status == 'in_progress':
            position = Position.objects.create(run=run_id, latitude=latitude, longitude=longitude)
            return Response({'message': 'Все ништяк'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Забег не начат или закончен'}, status=status.HTTP_400_BAD_REQUEST)


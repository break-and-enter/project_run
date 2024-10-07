from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Run, Position
from .serializers import RunSerializer, PositionSerializer
from haversine import haversine
from geopy.distance import geodesic


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
        # НЕ ЗАБЫТЬ РАСКОММЕНТИРОВАТЬ !!
        run.status = 'finished'
        run.save()
        positions_qs = Position.objects.filter(run=run_id)
        positions_quantity = len(positions_qs) # Количество записанных координат
        distance = 0
        for i in range(positions_quantity-1):
            distance += geodesic((positions_qs[i].latitude,positions_qs[i].longitude), (positions_qs[i+1].latitude,positions_qs[i+1].longitude)).kilometers

        # distance = haversine(start_positions, end_positions)
        # print(distance)
        run.distance = distance
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


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

    def get_queryset(self):
        qs = self.queryset
        run_id = self.request.query_params.get('run')
        if run_id:
            qs = qs.filter(run=run_id)
        return qs



from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from .models import Run, Position, Subscription
from .serializers import RunSerializer, PositionSerializer, UserSerializer
from geopy.distance import geodesic
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.select_related('athlete').all()
    serializer_class = RunSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'id']
    ordering_fields = ['created_at']


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
        #Добавлю условие чтобы не вылетало исключение когда делаю задачу которая идет ДО создания позиций
        #А МОЖНО ПРОСТО ВРЕМЕННО ЗАКОММЕНТИРОВАТЬ ВСЕ ДО run.save()
        if Position.objects.filter(run=run_id).exists():
            positions_qs = Position.objects.filter(run=run_id)
            positions_quantity = len(positions_qs)
            distance = 0
            for i in range(positions_quantity-1):
                distance += geodesic((positions_qs[i].latitude,positions_qs[i].longitude), (positions_qs[i+1].latitude,positions_qs[i+1].longitude)).kilometers
            run.distance = distance
            # -----------------------------------------
            positions_qs_sorted_by_date = positions_qs.order_by('date_time')
            run_time = positions_qs_sorted_by_date[positions_quantity-1].date_time-positions_qs_sorted_by_date[0].date_time
            run.run_time_seconds = run_time.total_seconds()
            #-------------------------------------------
            average_speed = positions_qs.aggregate(Avg('speed'))
            run.speed = round(average_speed['speed__avg'], 2)
        run.save()
        #-------------------------------------------

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

    def perform_create(self, serializer):
        run = serializer.validated_data['run']
        serializer.save() # чтобы включить только что создаваемую позицию в QS
        all_positions = Position.objects.filter(run=run)
        if all_positions.count() > 1:

            ordered_positions = all_positions.order_by('-id')
            last_position = ordered_positions[0]
            previous_position = ordered_positions[1]
            previous_distance = previous_position.distance
            last_distance = geodesic((last_position.latitude, last_position.longitude),
                                 (previous_position.latitude, previous_position.longitude)).meters
            time_delta = last_position.date_time - previous_position.date_time
            speed = last_distance/time_delta.total_seconds()
            last_position.speed = round(speed, 2)
            last_position.distance = round(previous_distance + last_distance/1000, 2)
            last_position.save()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_superuser=False)
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'last_name']

    def get_queryset(self):
        qs = self.queryset
        user_type = self.request.query_params.get('type')
        if user_type and user_type=='coach':
            qs = qs.filter(is_staff=True)
        if user_type and user_type=='athlete':
            qs = qs.filter(is_staff=False)
        qs = qs.annotate(runs_finished=Count('run', filter=Q(run__status='finished')))
        return qs

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        print(instance.id, instance.username)
        print(serializer.data)

        if not instance.is_staff: # user is athlete
            if Subscription.objects.filter(athlete=instance.id).exists():
                subscription = Subscription.objects.get(athlete=instance.id)
                print(subscription.coach.id)
                my_data = serializer.data
                my_data['coach'] = subscription.coach.id
                return Response(my_data)
        else: # user is coach
            if Subscription.objects.filter(coach=instance.id).exists():
                athletes_list = Subscription.objects.filter(coach=instance.id).values_list('id', flat=True)
                print(athletes_list)
                my_data = serializer.data
                my_data['athletes'] = athletes_list
                return Response(my_data)
        return Response(serializer.data)



class SubscribeView(APIView):
    def post(self, request, id):
        coach_id = id
        print(coach_id)
        athlete_id = self.request.data['athlete']
        print(athlete_id)
        if not User.objects.filter(id=coach_id).exists():
            return Response({'message': f'Пользователя c id {coach_id} не существует'},
                            status=status.HTTP_404_NOT_FOUND)
        if not User.objects.filter(id=athlete_id).exists():
            return Response({'message': f'Пользователя c id {athlete_id} не существует'},
                            status=status.HTTP_400_BAD_REQUEST)
        coach=User.objects.get(id=coach_id)
        athlete=User.objects.get(id=athlete_id)
        if not coach.is_staff:
        # if coach.type != 'coach':
            return Response({'message': f'Пользователь c id {coach_id} это не тренер'}, status=status.HTTP_400_BAD_REQUEST)
        if athlete.is_staff:
        # if athlete.type != 'athlete':
            return Response({'message': f'Пользователь c id {coach_id} это не бегун'}, status=status.HTTP_400_BAD_REQUEST)
        if Subscription.objects.filter(coach=coach, athlete=athlete).exists():
            return Response({'message': 'Такая подписка уже существует'},
                            status=status.HTTP_400_BAD_REQUEST)
        Subscription.objects.create(coach=coach, athlete=athlete)

        return Response({'message': 'Все ништяк'}, status=status.HTTP_200_OK)


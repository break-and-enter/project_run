from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from .models import Run, Position, Subscription, Challenge
from .serializers import RunSerializer, PositionSerializer, UserSerializer, AthleteSerializer, CoachSerializer, \
    ChallengeSerializer
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
        if Run.objects.filter(status='finished', athlete=run.athlete).count() >= 10:
            challenge, created = Challenge.objects.get_or_create(full_name = 'Сделай 10 Забегов!', athlete=run.athlete)
        #-------------------------------------------
        distance_sum = Run.objects.filter(status='finished', athlete=run.athlete).aggregate(Sum('distance'))

        if distance_sum['distance__sum'] >= 50:
            challenge, created = Challenge.objects.get_or_create(full_name = 'Пробеги 50 километров!', athlete=run.athlete)
        #-------------------------------------------
        if run.distance >= 2 and run.run_time_seconds <= 600:
            challenge, created = Challenge.objects.get_or_create(full_name='Пробеги 2 километра меньше чем за 10 минут!',
                                                                 athlete=run.athlete)
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

    def get_serializer_class(self):
        if self.action == 'list':
            return UserSerializer
        elif self.action == 'retrieve':
            user = self.get_object() # крутой метод! почему я его не знал!!
            if user.is_staff:
                return CoachSerializer
            else:
                return AthleteSerializer
        return super().get_serializer_class()


class SubscribeView(APIView):
    def post(self, request, id):
        coach_id = id
        athlete_id = self.request.data['athlete']

        coach = get_object_or_404(User, id=coach_id)
        if not User.objects.filter(id=athlete_id).exists():
            return Response({'message': f'Пользователя c id {athlete_id} не существует'},
                            status=status.HTTP_400_BAD_REQUEST)
        athlete=User.objects.get(id=athlete_id)

        if not coach.is_staff:
            return Response({'message': f'Пользователь c id {coach_id} это не тренер'}, status=status.HTTP_400_BAD_REQUEST)
        if athlete.is_staff:
            return Response({'message': f'Пользователь c id {coach_id} это не бегун'}, status=status.HTTP_400_BAD_REQUEST)
        if Subscription.objects.filter(coach=coach, athlete=athlete).exists():
            return Response({'message': 'Такая подписка уже существует'},
                            status=status.HTTP_400_BAD_REQUEST)
        Subscription.objects.create(coach=coach, athlete=athlete)

        return Response({'message': 'Все ништяк'}, status=status.HTTP_200_OK)


class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['athlete']


@api_view(['GET'])
def challenge_summary_view(request):
    # Получим список уникальных названий челленджей
    unique_challenges = Challenge.objects.values('full_name').distinct()
    unique_name_list = [i['full_name'] for i in unique_challenges]

    #Получим список атлетов для каждого челленджа
    final_list = []
    for challenge_name in unique_name_list:
        user_queryset = User.objects.filter(challenge__full_name=challenge_name)
        athletes_list = []
        for athlete in user_queryset:
            athletes_list.append({'id': athlete.id, 'full_name': f'{athlete.first_name} {athlete.last_name}'})

        final_list.append({'name_to_display':challenge_name, 'athletes':athletes_list})

    return Response(final_list)

    # return Response([{'name_to_display': 'Сделай 10 Забегов!', 'athletes': [{'id': 3, 'full_name': 'иван иванович'}]},
    #                  {'name_to_display': 'Пробеги 50 километров!', 'athletes': [{'id': 3, 'full_name': 'иван иванович'}]},
    #                  {'name_to_display': 'Пробеги 2 километра меньше чем за 10 минут!',
    #                   'athletes': [{'id': 3, 'full_name': 'иван иванович'}]}
    #                  ])

class CoachRatingView(APIView):
    def post(self, request, coach_id):
        athlete_id = request.data.get('athlete')
        rating = request.data.get('rating')
        if not athlete_id:
            return Response({'message': f'Нет поля athlete_id'}, status=status.HTTP_400_BAD_REQUEST)

        if not rating:
            return Response({'message': f'Нет поля rating'}, status=status.HTTP_400_BAD_REQUEST)

        # if not rating.isdigit():
        #     return Response({'message': f'rating должен быть цифрой'}, status=status.HTTP_400_BAD_REQUEST)

        if rating and 1<= int(rating) <=5:
            return Response({'message': 'rating не в пределах от 1 до 5'}, status=status.HTTP_400_BAD_REQUEST)

        # print(athlete_id)
        if Subscription.objects.filter(coach=coach_id, athlete=athlete_id).exists():
            subscription = Subscription.objects.get(coach=coach_id, athlete=athlete_id)

            subscription.rating = rating
            subscription.save()
        else:

            return Response({'message':f'Бегун c id {athlete_id} не подписан на тренера с id {coach_id}'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'ОК'})
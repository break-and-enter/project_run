from django.db.models import Avg
from rest_framework import serializers
from .models import Run, Position, Subscription, Challenge
from django.contrib.auth.models import User


class SmallUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class RunSerializer(serializers.ModelSerializer):
    athlete_data = SmallUserSerializer(source='athlete', read_only=True)

    class Meta:
        model = Run
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    date_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S.%f")
    class Meta:
        model = Position
        fields = '__all__'

    def validate(self, data):
        run = data.get('run')
        if run.status != 'in_progress':
            raise serializers.ValidationError('Забег должен быть начат и еще не закончен')
        return data

    def validate_latitude(self, value):
        if value > 90 or value < -90:
            raise serializers.ValidationError('latitude должен быть в диапазоне от -90.0 до +90.0 градусов')
        return value

    def validate_longitude(self, value):
        if value > 180 or value < -180:
            raise serializers.ValidationError('longitude должен быть в диапазоне от -180.0 до +180.0 градусов')
        return value


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.IntegerField()
    rating = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'type', 'runs_finished', 'rating']

    def get_type(self, obj):
        if obj.is_staff:
            return 'coach'
        else:
            return 'athlete'

    def get_rating(self, obj):
        if obj.is_staff:
            result = Subscription.objects.filter(coach=obj.id).aggregate(Avg('rating'))
            return result['rating__avg']
        return None


class AthleteSerializer(UserSerializer):
    coach = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['coach']

    def get_coach(self, obj):
        if Subscription.objects.filter(athlete=obj.id).exists():
            subscription = Subscription.objects.get(athlete=obj.id)
            return subscription.coach.id
        return ''


class CoachSerializer(UserSerializer):
    athletes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['athletes']

    def get_athletes(self, obj):
        #Возвращает пустой список если ничего не найдено удовлетворяющее фильтру
        athletes_list = Subscription.objects.filter(coach=obj.id).values_list('athlete__id', flat=True)
        return athletes_list

class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = '__all__'
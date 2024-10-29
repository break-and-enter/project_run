from rest_framework import serializers
from .models import Run, Position
from django.contrib.auth.models import User



class SmallUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class RunSerializer(serializers.ModelSerializer):
    athlete_data = serializers.SerializerMethodField()
    class Meta:
        model = Run
        fields = '__all__'

    def get_athlete_data(self, obj):
        # return SmallUserSerializer(obj.athlete).data
        athlete = obj.athlete
        return {
            'id' : athlete.id,
            'username': athlete.username,
            'first_name' : athlete.first_name,
            'last_name': athlete.last_name,
            }


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
    # runs_finished = serializers.SerializerMethodField()
    runs_finished = serializers.IntegerField()
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'type', 'runs_finished']

    def get_type(self, obj):
        if obj.is_staff:
            return 'coach'
        else:
            return 'athlete'

    # def get_runs_finished(self, obj):
    #     user_id = obj.id
    #     runs_finished = Run.objects.filter(athlete=user_id, status='finished').count()
    #
    #     return runs_finished



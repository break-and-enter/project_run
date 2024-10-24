from rest_framework import serializers
from .models import Run, Position
from django.contrib.auth.models import User


class RunSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = User
        fields = '__all__'
from rest_framework import serializers
from .models import Task, User, Application

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('resident', 'latitude', 'longitude')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_student', 'is_resident')

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ('student', 'status')

class TaskDetailSerializer(TaskSerializer):
    applications = ApplicationSerializer(many=True, read_only=True)
from rest_framework import serializers
from .models import Task, User, Application

class TaskSerializer(serializers.ModelSerializer):
    has_accepted_applicants = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ("tasker", "latitude", "longitude", "has_accepted_applicants")


# core/serializers.py
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"
        read_only_fields = ("student", "status")


class TaskDetailSerializer(TaskSerializer):
    applications = ApplicationSerializer(many=True, read_only=True)

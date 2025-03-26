from rest_framework.response import Response
from .permissions import IsResident, IsStudent, IsTaskOwnerOrReadOnly
from .models import Application, Task
from .serializers import ApplicationSerializer, TaskSerializer, TaskDetailSerializer
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    permission_classes = [IsTaskOwnerOrReadOnly | permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TaskDetailSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_resident:
            raise PermissionDenied("Only residents can post tasks.")
        serializer.save(resident=self.request.user)

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated | permissions.IsAdminUser]

    def perform_create(self, serializer):
        if not self.request.user.is_student:
            raise PermissionDenied("Only students can apply.")
        serializer.save(student=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[IsResident])
    def accept(self, request, pk=None):
        application = self.get_object()
        if application.task.resident != request.user:
            raise PermissionDenied("Only task owner can accept applications.")
        application.status = 'accepted'
        application.save()
        application.task.status = 'in_progress'
        application.task.save()
        return Response({'status': 'accepted'})
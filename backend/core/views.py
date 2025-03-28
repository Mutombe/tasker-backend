from rest_framework.response import Response
from .permissions import IsResident, IsStudent, IsTaskOwnerOrReadOnly
from .models import Application, Task, User
from .serializers import ApplicationSerializer, TaskSerializer, TaskDetailSerializer
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import UserSerializer
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework import viewsets, permissions, status
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import UserSerializer
import logging

logger = logging.getLogger(__name__)
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_active=True)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            context = {
                "username": user.username,
                "verification_url": f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/",
                "support_email": settings.SUPPORT_EMAIL,
            }

            html_message = render_to_string("email_verify.html", context)
            plain_message = strip_tags(html_message)

            send_mail(
                "Verify your Taskoba account",
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )

            return Response(
                {"detail": "Verification email sent - please check your inbox"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Standard token validation
        data = super().validate(attrs)
        
        # Add user details to the response
        user = self.user
        user_serializer = UserSerializer(user)
        
        # Include user details in the response
        data['user'] = user_serializer.data
        
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response(
                {"detail": "Email successfully verified"}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "Invalid verification link"}, status=status.HTTP_400_BAD_REQUEST
        )


class ResendVerificationView(APIView):
    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response(
                    {"detail": "Account is already active"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Resend verification email (same logic as RegisterView)
            # ... [reuse email sending code from RegisterView] ...

            return Response(
                {"detail": "Verification email resent successfully"},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "User with this email does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

class TaskViewSet(viewsets.ModelViewSet):

    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TaskDetailSerializer
        return TaskSerializer

    #def perform_create(self, serializer):
     #   serializer.save(tasker=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        logger.error(f"User in request: {user}")
        logger.error(f"User is authenticated: {user.is_authenticated}")
        
        if not user.is_authenticated:
            logger.error("Attempt to create task with unauthenticated user")
            raise ValueError("Authentication required to create a task")
        
        serializer.save(tasker=user)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        if task.has_accepted_applicants:
            return Response(
                {"detail": "Cannot delete task with accepted applicants."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        task = self.get_object()
        if task.has_accepted_applicants:
            return Response(
                {"detail": "Cannot update task with accepted applicants."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated | permissions.IsAdminUser]

    def perform_create(self, serializer):
        if not self.request.user.is_student:
            raise PermissionDenied("Only students can apply.")
        serializer.save(student=self.request.user)

    @action(detail=True, methods=["patch"], permission_classes=[IsResident])
    def accept(self, request, pk=None):
        application = self.get_object()
        if application.task.tasker != request.user:
            raise PermissionDenied("Only task owner can accept applications.")
        application.status = "accepted"
        application.save()
        application.task.status = "in_progress"
        application.task.save()
        return Response({"status": "accepted"})

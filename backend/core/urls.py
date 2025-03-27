from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import (
    TaskViewSet,
    ApplicationViewSet,
    RegisterView,
    VerifyEmailView,
    ResendVerificationView,
)
from rest_framework.routers import DefaultRouter
from .views import CustomTokenObtainPairView

router = DefaultRouter()
router.register(r"tasks", TaskViewSet)
router.register(r"applications", ApplicationViewSet, basename="application")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", CustomTokenObtainPairView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),

    path(
        "auth/verify-email/<str:uidb64>/<str:token>/",
        VerifyEmailView.as_view(),
        name="verify-email",
    ),
    path(
        "auth/resend-verification/",
        ResendVerificationView.as_view(),
        name="resend-verification",
    ),
]

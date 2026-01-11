from django.urls import include, path
from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import CreatePaymentView, PaymentStatusView, UserCreateAPIView, UserViewSet

app_name = UsersConfig.name

router = SimpleRouter()
router.register("users", UserViewSet, basename="user")
# router.register("payments", PaymentViewSet, basename="payment")


urlpatterns = [
    path("", include(router.urls)),
    path("register/", UserCreateAPIView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name="login"),
    path("payments/create/", CreatePaymentView.as_view(), name="payment-create"),
    path("payments/status/<str:session_id>/", PaymentStatusView.as_view(), name="payment-status"),
    path("token/refresh/", TokenRefreshView.as_view(permission_classes=(AllowAny,)), name="token_refresh"),
]

from django.urls import path
# from dj_rest_auth.views import (
#     LoginView,
#     PasswordChangeView,
#     PasswordResetView,
#     PasswordResetConfirmView,
#     LogoutView,
# )
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    CrewMemberLoginView,
    CrewMemberRegistrationView,
    ClientLoginView,
    ClientRegistrationView,
    LogoutView
)


app_name = "kopero_auth"
urlpatterns = [
    path('register/crew-member/', CrewMemberRegistrationView.as_view(), name="register_crew_member"),
    path("register/client/", ClientRegistrationView.as_view(), name="register_customer"),
    path("login/crew-member/", CrewMemberLoginView.as_view(), name="login_crew_member"),
    path("login/client/", ClientLoginView.as_view(), name="login_client"),
    path("logout/", LogoutView.as_view(), name="logout") 
]

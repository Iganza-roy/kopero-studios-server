from django.urls import path
from dj_rest_auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
    LogoutView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# from .adapter import respond_email_verification_sent
from dj_rest_auth.registration.views import RegisterView
from kopero_auth.views import (
    UsersListView,
    UserDetailView,
    RegisterNonAdminUSerView,
    # TokenBasedLoginView,
    # migrate_stuff,
    create_auth_token,
)

app_name = "kopero_auth"
urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password/reset/", PasswordResetView.as_view(), name="password_reset"),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),

   
    path('token/create/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path("email-verification-sent/", respond_email_verification_sent, name="account_email_verification_sent"),
    path("password/change/", PasswordChangeView.as_view(), name="change"),
    path("users/", UsersListView.as_view(), name="users"),
    path("users/<uuid:pk>/", UserDetailView.as_view(), name="user_details"),
    path("users/details/", UserDetailView.as_view(), name="own_details"),
]
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    CrewMemberLoginView,
    CrewMemberRegistrationView,
    ClientLoginView,
    ClientRegistrationView,
    LogoutView,
    CrewDetailView,
    ClientDetailView,
    ClientsListView,
    CrewsListView,
)


app_name = "kopero_auth"
urlpatterns = [
    path('register/crew/', CrewMemberRegistrationView.as_view(), name="register_crew_member"),
    path("register/client/", ClientRegistrationView.as_view(), name="register_customer"),
    path("login/crew/", CrewMemberLoginView.as_view(), name="login_crew_member"),
    path("login/client/", ClientLoginView.as_view(), name="login_client"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path("clients/", ClientsListView.as_view(), name="clients"),
    path("clients/<uuid:pk>/", ClientDetailView.as_view(), name="client_details"),
    path("crews/", CrewsListView.as_view(), name="crews"),
    path("crews/<uuid:pk>/", CrewDetailView.as_view(), name="crew_details")
]

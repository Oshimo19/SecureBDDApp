from django.urls import path
from . import views # Importe les vues definies dans accounts/views.py

urlpatterns = [
    path("home/", views.HomeView.as_view(), name="home"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("user/me/", views.UserProfileView.as_view(), name="user-me"),
    path("admin/users/", views.AdminListUsersView.as_view(), name="admin-users"),
    path("admin/users/delete/<int:user_id>", views.AdminDeleteUserView.as_view(), name="admin-delete-user"),
]

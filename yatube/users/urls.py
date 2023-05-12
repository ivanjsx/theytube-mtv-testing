from django.contrib.auth import views
from django.urls import path, reverse_lazy

from .views import SignUpView

app_name: str = "users"

urlpatterns = [
    path(route="signup/", view=SignUpView.as_view(), name="signup"),

    path(
        route="login/",
        view=views.LoginView.as_view(
            template_name="users/login.html"
        ),
        name="login",
    ),
    path(
        route="logout/",
        view=views.LogoutView.as_view(
            template_name="users/logout.html"
        ),
        name="logout",
    ),

    path(
        route="password_change/",
        view=views.PasswordChangeView.as_view(
            template_name="users/password_change.html",
            success_url=reverse_lazy(viewname="users:password_change_done")
        ),
        name="password_change",
    ),
    path(
        route="password_change/done/",
        view=views.PasswordChangeDoneView.as_view(
            template_name="users/password_change_done.html"
        ),
        name="password_change_done",
    ),

    path(
        route="password_reset/",
        view=views.PasswordResetView.as_view(
            template_name="users/password_reset.html",
            email_template_name="users/password_reset_email.html",
            success_url=reverse_lazy(viewname="users:password_reset_done")
        ),
        name="password_reset",
    ),
    path(
        route="password_reset/done/",
        view=views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),

    # TODO fix /auth/password_reset/confirm/ path
    path(
        route="password_reset/confirm/<uidb64>/<token>/",
        view=views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url=reverse_lazy(viewname="users:password_reset_complete")
        ),
        name="password_reset_confirm",
    ),
    path(
        route="password_reset/complete/",
        view=views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]

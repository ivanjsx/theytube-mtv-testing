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
        route="change/",
        view=views.PasswordChangeView.as_view(
            template_name="users/change.html",
            success_url=reverse_lazy(viewname="users:change_done")
        ),
        name="change",
    ),
    path(
        route="change/done/",
        view=views.PasswordChangeDoneView.as_view(
            template_name="users/change_done.html"
        ),
        name="change_done",
    ),

    path(
        route="reset/",
        view=views.PasswordResetView.as_view(
            template_name="users/reset.html",
            email_template_name="users/reset_email.html",
            success_url=reverse_lazy(viewname="users:reset_done")
        ),
        name="reset",
    ),
    path(
        route="reset/done/",
        view=views.PasswordResetDoneView.as_view(
            template_name="users/reset_done.html"
        ),
        name="reset_done",
    ),

    # TODO fix /auth/reset/confirm/ path
    path(
        route="reset/confirm/<uidb64>/<token>/",
        view=views.PasswordResetConfirmView.as_view(
            template_name="users/reset_confirm.html",
            success_url=reverse_lazy(viewname="users:reset_complete")
        ),
        name="reset_confirm",
    ),
    path(
        route="reset/complete/",
        view=views.PasswordResetCompleteView.as_view(
            template_name="users/reset_complete.html"
        ),
        name="reset_complete",
    ),
]

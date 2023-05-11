from django.urls import path

from . import views

app_name: str = "about"

urlpatterns = [
    path(
        route="author/",
        view=views.AuthorView.as_view(),
        name="author"
    ),
    path(
        route="tech/",
        view=views.TechView.as_view(),
        name="tech"
    ),
]

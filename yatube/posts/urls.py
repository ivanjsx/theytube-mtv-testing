from django.urls import path

from . import views

app_name: str = "posts"

urlpatterns = [
    path(route="", view=views.index, name="index"),

    path(
        route="follow/",
        view=views.follow_index,
        name="follow_index"
    ),

    path(
        route="group/<slug:slug>/",
        view=views.group_posts,
        name="group_posts",
    ),

    path(
        route="profile/<str:username>/",
        view=views.profile,
        name="profile",
    ),
    path(
        route="profile/<str:username>/follow/",
        view=views.profile_follow,
        name="profile_follow",
    ),
    path(
        route="profile/<str:username>/unfollow/",
        view=views.profile_unfollow,
        name="profile_unfollow",
    ),

    path(
        route="posts/<int:post_id>/",
        view=views.post_detail,
        name="post_detail",
    ),

    path(
        route="create/",
        view=views.post_create,
        name="post_create",
    ),
    path(
        route="posts/<int:post_id>/edit/",
        view=views.post_edit,
        name="post_edit",
    ),
    path(
        route="posts/<int:post_id>/comment/",
        view=views.add_comment,
        name="add_comment"
    ),
]

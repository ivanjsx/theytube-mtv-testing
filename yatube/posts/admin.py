from django.contrib import admin

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Настройка отображения объектов Post в django-админке."""

    list_display = (
        "pk",
        "created",
        "text",
        "author",
        "group",
        "image",
        "comments",
    )

    ordering = ("-created", )
    search_fields = ("text", )
    list_editable = ("group", )
    list_filter = ("created", )

    empty_value_display = "-пусто-"


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Настройка отображения объектов Group в django-админке."""

    list_display = (
        "pk",
        "title",
        "description",
        "slug",
        "posts",
    )

    search_fields = ("title", "description", )
    ordering = ("slug", )

    empty_value_display = "-пусто-"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Настройка отображения объектов Comment в django-админке."""

    list_display = (
        "pk",
        "created",
        "text",
        "post",
        "author",
    )

    ordering = ("-created", )
    search_fields = ("text", )
    list_filter = ("created", )

    empty_value_display = "-пусто-"


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Настройка отображения объектов Follow в django-админке."""

    list_display = (
        "pk",
        "created",
        "user",
        "author",
    )

    ordering = ("-created", )
    search_fields = ("user", "author", )
    list_filter = ("created", )

    empty_value_display = "-пусто-"

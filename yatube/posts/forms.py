from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования постов (объектов Post)."""

    class Meta:
        model = Post
        fields = ("text", "group", "image")


class CommentForm(forms.ModelForm):
    """Форма для создания и редактирования комментариев (объектов Comment)."""

    class Meta:
        model = Comment
        fields = ("text",)

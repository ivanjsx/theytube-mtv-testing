from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_page

from .constants import CACHE_TIMEOUT_SECONDS
from .forms import CommentForm, PostForm
from .helpers import paginate
from .models import Follow, Group, Post

User = get_user_model()


@cache_page(timeout=CACHE_TIMEOUT_SECONDS, key_prefix="index_page")
def index(request: HttpRequest) -> HttpResponse:
    """
    Главная страница.
    Отображает постранично все опубликованные записи (объекты Post).
    Посты идут в порядке убывания даты публикации.
    """

    posts = Post.objects.all()
    return render(
        request=request,
        template_name="posts/index.html",
        context={"page_obj": paginate(request=request, queryset=posts)},
    )


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Страница Сообщества (объекта Group).
    Отображает постранично все опубликованные в нём записи (объекты Post).
    Посты идут в порядке убывания даты публикации.
    """

    group = get_object_or_404(klass=Group, slug=slug)
    posts = group.posts.all()
    return render(
        request=request,
        template_name="posts/group_list.html",
        context={
            "group": group,
            "page_obj": paginate(request=request, queryset=posts),
        }
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """
    Страница Пользователя (объекта User).
    Отображает постранично все опубликованные им записи (объекты Post).
    Посты идут в порядке убывания даты публикации.
    """

    author = get_object_or_404(klass=User, username=username)
    posts = author.posts.all()

    following = (
        Follow.objects.filter(
            user=request.user, author=author,
        ).exists()
        if request.user.is_authenticated
        else False
    )

    return render(
        request=request,
        template_name="posts/profile.html",
        context={
            "author": author,
            "following": following,
            "page_obj": paginate(request=request, queryset=posts),
        }
    )


@cache_page(timeout=CACHE_TIMEOUT_SECONDS, key_prefix="post_page")
def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """Страница отдельного поста (объекта Post)."""

    post = get_object_or_404(klass=Post, id=post_id)
    form = CommentForm()

    return render(
        request=request,
        template_name="posts/post_detail.html",
        context={
            "post": post,
            "form": form,
        },
    )


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    """Создать пост (объект Post) через интерфейс проекта."""

    form = PostForm(
        data=(request.POST or None),
        files=(request.FILES or None),
    )

    if not form.is_valid():
        return render(
            request=request,
            template_name="posts/post_create.html",
            context={"form": form},
        )

    post = form.save(commit=False)
    post.author = request.user
    post.save()

    return redirect(
        to=reverse_lazy(
            viewname="posts:profile",
            kwargs={"username": request.user.username},
        )
    )


@login_required
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    """Редактировать пост (объект Post) через интерфейс проекта."""

    post = get_object_or_404(klass=Post, id=post_id)
    form = PostForm(
        data=(request.POST or None),
        files=(request.FILES or None),
        instance=post,
    )

    if post.author != request.user:
        return redirect(
            to=reverse_lazy(
                viewname="posts:post_detail",
                kwargs={"post_id": post_id},
            )
        )

    if not form.is_valid():
        return render(
            request=request,
            template_name="posts/post_create.html",
            context={"form": form, "post_id": post_id},
        )

    form.save()
    return redirect(
        to=reverse_lazy(
            viewname="posts:post_detail",
            kwargs={"post_id": post_id},
        ),
    )


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    """
    Добавить коментарий (объект comment) под постом (объектом Post)
    через интерфейс проекта.
    """

    post = get_object_or_404(klass=Post, id=post_id)
    form = CommentForm(
        data=(request.POST or None)
    )

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect(
        to=reverse_lazy(
            viewname="posts:post_detail",
            kwargs={"post_id": post_id},
        ),
    )


@login_required
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    """
    Подписаться (создать объект Follow) на автора (объекта User)
    через интерфейс проекта (на странице профиля автора).
    """

    author = get_object_or_404(klass=User, username=username)

    if request.user != author and not Follow.objects.filter(
        user=request.user, author=author,
    ).exists():
        Follow.objects.create(user=request.user, author=author)

    return redirect(to=reverse_lazy(viewname="posts:profile",
                                    kwargs={"username": username}))


@login_required
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    """
    Отписаться (удалить объект Follow) от автора (объекта User)
    через интерфейс проекта (на странице профиля автора).
    """

    author = get_object_or_404(klass=User, username=username)

    if request.user != author and Follow.objects.filter(
        user=request.user, author=author,
    ).exists():
        Follow.objects.filter(user=request.user, author=author).delete()

    return redirect(to=reverse_lazy(viewname="posts:profile",
                                    kwargs={"username": username}))


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    """
    Страница с постами только тех авторов,
    на которых подписан пользователь.
    """

    follower = request.user.follower.all().values("author")
    posts = Post.objects.filter(author__in=follower)

    return render(
        request=request,
        template_name="posts/follow.html",
        context={"page_obj": paginate(request=request, queryset=posts)},
    )

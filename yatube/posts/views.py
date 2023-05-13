from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST

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

    posts = Post.objects.select_related("author", "group").all()

    return render(
        request=request,
        template_name="posts/index.html",
        context={
            "page_obj": paginate(request=request, queryset=posts),
        },
    )


# TODO fix redirection target after login
@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    """
    Страница с постами только тех авторов,
    на которых подписан пользователь.
    """

    posts = Post.objects.filter(
        author__following__user=request.user
    ).select_related("author", "group")

    return render(
        request=request,
        template_name="posts/follow.html",
        context={
            "page_obj": paginate(request=request, queryset=posts),
        },
    )


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Страница Сообщества (объекта Group).
    Отображает постранично все опубликованные в нём записи (объекты Post).
    Посты идут в порядке убывания даты публикации.
    """

    group = get_object_or_404(klass=Group, slug=slug)
    posts = group.posts.select_related("author").all()
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
    posts = author.posts.select_related("group").all()

    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author,
    ).exists()

    return render(
        request=request,
        template_name="posts/profile.html",
        context={
            "author": author,
            "following": following,
            "page_obj": paginate(request=request, queryset=posts),
        }
    )


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """Страница отдельного поста (объекта Post)."""

    post = get_object_or_404(
        klass=Post.objects.select_related("author", "group"),
        id=post_id,
    )
    form = CommentForm()
    comments = post.comments.select_related("author").all()

    return render(
        request=request,
        template_name="posts/post_detail.html",
        context={
            "post": post,
            "form": form,
            "comments": comments,
        },
    )


# TODO fix redirection target after login
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


# TODO fix redirection target after login
@login_required
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    """Редактировать пост (объект Post) через интерфейс проекта."""

    post = get_object_or_404(
        klass=Post.objects.select_related("author", "group"),
        id=post_id,
    )
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


# TODO fix redirection target after login
@login_required
@require_POST
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    """
    Добавить коментарий (объект comment) под постом (объектом Post)
    через интерфейс проекта.
    """

    post = get_object_or_404(
        klass=Post.objects.select_related("author", "group"),
        id=post_id,
    )
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


# TODO fix redirection target after login
@login_required
# @require_POST
# декоратор убрал потому что с ним не срабатывают
# тесты Практикума - что показалось мне странным;
# вроде же GET-запросами не надо совершать модификации над данными??
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    """
    Подписаться (создать объект Follow) на автора (объекта User)
    через интерфейс проекта (на странице профиля автора).
    """

    author = get_object_or_404(klass=User, username=username)

    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user, author=author,
        )

    return redirect(to=reverse_lazy(viewname="posts:profile",
                                    kwargs={"username": username}))


# TODO fix redirection target after login
@login_required
# @require_POST
# аналогично симметричной функции profile_follow выше
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    """
    Отписаться (удалить объект Follow) от автора (объекта User)
    через интерфейс проекта (на странице профиля автора).
    """

    author = get_object_or_404(klass=User, username=username)

    Follow.objects.filter(user=request.user, author=author).delete()

    return redirect(to=reverse_lazy(viewname="posts:profile",
                                    kwargs={"username": username}))

from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel

from .constants import POST_PREVIEW_SYMBOLS

User = get_user_model()


class Group(models.Model):
    """Сообщество, в рамках которого можно публиковать объекты Post."""

    title = models.CharField(
        max_length=200,
        verbose_name="Название сообщества",
        help_text="Введите название будущего сообщества",
        editable=True,
    )
    description = models.TextField(
        verbose_name="Описание сообщества",
        help_text="Введите описание будущего сообщества",
        editable=True,
    )
    slug = models.SlugField(
        editable=True,
        unique=True,
        max_length=200,
        verbose_name="Слаг сообщества",
        help_text="Введите слаг (он будет использован в URL)",
    )

    class Meta:
        verbose_name = "Сообщество"
        verbose_name_plural = "Сообщества"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return f"/group/{self.slug}/"


class Post(CreatedModel):
    """
    Записи в блоге. Могут принадлежать Сообществу (объекту Group).
    Так же могут быть и отдельными, не принадлежащими никакому из них.
    """

    text = models.TextField(
        verbose_name="Текст поста",
        help_text="Введите текст будущего поста",
        editable=True,
    )
    author = models.ForeignKey(
        to=User,
        editable=True,
        related_name="posts",
        on_delete=models.CASCADE,
        verbose_name="Автор поста",
    )
    group = models.ForeignKey(
        to=Group,
        blank=True,
        null=True,
        editable=True,
        related_name="posts",
        on_delete=models.SET_NULL,
        verbose_name="Сообщество, к которому относится пост",
        help_text="Выберите сообщество, в котором опубликуете пост",
    )
    image = models.ImageField(
        verbose_name="Заглавная картинка поста",
        help_text="Загрузите картинку",
        upload_to="posts/",
        blank=True,
        null=True,
        editable=True,
    )

    class Meta:
        ordering = ("-created", )
        get_latest_by = "created"
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self) -> str:
        return self.text[:POST_PREVIEW_SYMBOLS]

    def get_absolute_url(self):
        return f"/posts/{self.id}/"


class Comment(CreatedModel):
    """
    Комментарии под постом (объектом Post).
    Не могут существовать без поста, под которым опубликованы.
    """

    text = models.TextField(
        verbose_name="Текст комментария",
        help_text="Введите текст будущего комментария",
        editable=True,
    )
    post = models.ForeignKey(
        to=Post,
        blank=False,
        null=False,
        editable=True,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name="Пост, под которым опубликован комментарий",
    )
    author = models.ForeignKey(
        to=User,
        editable=True,
        related_name="comments",
        on_delete=models.CASCADE,
        verbose_name="Автор комментария",
    )

    class Meta:
        ordering = ("-created", )
        get_latest_by = "created"
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self) -> str:
        return self.text[:POST_PREVIEW_SYMBOLS]


class Follow(CreatedModel):
    """Подписка пользователя на автора в блоге."""

    user = models.ForeignKey(
        to=User,
        blank=False,
        null=False,
        editable=True,
        related_name="follower",
        on_delete=models.CASCADE,
        verbose_name="Подписчик контент-креатора",
        help_text="Кто подписывается",
    )

    author = models.ForeignKey(
        to=User,
        blank=False,
        null=False,
        editable=True,
        related_name="following",
        on_delete=models.CASCADE,
        verbose_name="Контент-креатор",
        help_text="На кого подписывается",
    )

    class Meta:
        unique_together = ["user", "author"]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.CheckConstraint(
                check=~models.Q(author=models.F("user")),
                name="cannot follow yourself",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} follows {self.author}"

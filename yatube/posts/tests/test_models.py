from django.contrib.auth import get_user_model
from django.test import TestCase

from ..constants import COMMENT_PREVIEW_SYMBOLS, POST_PREVIEW_SYMBOLS
from ..models import Comment, Follow, Group, Post

User = get_user_model()


class GroupModelTest(TestCase):
    """Набор тестов для валидации модели Group."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title="Тестовая группа",
            description="Тестовое описание",
            slug="test_slug",
        )

        cls.fields_verbose_names = {
            "title": "Название сообщества",
            "description": "Описание сообщества",
            "slug": "Слаг сообщества",
        }

        cls.fields_help_texts = {
            "title": "Введите название будущего сообщества",
            "description": "Введите описание будущего сообщества",
            "slug": "Введите слаг (он будет использован в URL)",
        }

    def test_group_object_name_is_title_fild(self):
        """У модели Group корректно работает __str__."""

        self.assertEqual(
            first=self.group.title,
            second=str(self.group),
        )

    def test_group_model_fields_verbose_names(self):
        """verbose_name в полях модели Group совпадает с ожидаемым."""

        for value, expected in self.fields_verbose_names.items():
            with self.subTest(value=value):
                self.assertEqual(
                    first=self.group._meta.get_field(
                        field_name=value
                    ).verbose_name,
                    second=expected,
                )

    def test_group_model_fields_help_texts(self):
        """help_text в полях модели Group совпадает с ожидаемым."""

        for value, expected in self.fields_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    first=self.group._meta.get_field(
                        field_name=value
                    ).help_text,
                    second=expected,
                )


class PostModelTest(TestCase):
    """Набор тестов для валидации модели Post."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username="test_username",
        )
        cls.own_post = Post.objects.create(
            text="Тестовый текст поста тестового пользователя",
            author=cls.user,
        )

        cls.fields_verbose_names = {
            "created": "Дата и время создания",
            "text": "Текст поста",
            "author": "Автор поста",
            "group": "Сообщество, к которому относится пост",
            "image": "Заглавная картинка поста",
        }

        cls.fields_help_texts = {
            "text": "Введите текст будущего поста",
            "group": "Выберите сообщество, в котором опубликуете пост",
            "image": "Загрузите картинку",
        }

    def test_post_object_name_is_first_symbols_preview(self):
        """У модели Post корректно работает __str__."""

        self.assertEqual(
            first=self.own_post.text[:POST_PREVIEW_SYMBOLS],
            second=str(self.own_post),
        )

    def test_post_model_fields_verbose_names(self):
        """verbose_name в полях модели Post совпадает с ожидаемым."""

        for value, expected in self.fields_verbose_names.items():
            with self.subTest(value=value):
                self.assertEqual(
                    first=self.own_post._meta.get_field(
                        field_name=value
                    ).verbose_name,
                    second=expected,
                )

    def test_post_model_fields_help_texts(self):
        """help_text в полях модели Post совпадает с ожидаемым."""

        for value, expected in self.fields_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    first=self.own_post._meta.get_field(
                        field_name=value
                    ).help_text,
                    second=expected,
                )


class CommentModelTest(TestCase):
    """Набор тестов для валидации модели Сomment."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username="test_username",
        )
        cls.post = Post.objects.create(
            text="Тестовый текст поста тестового пользователя",
            author=cls.user,
        )
        cls.comment = Comment.objects.create(
            text=("Тестовый текст комментария тестового пользователя "
                  "к тестовому посту"),
            post=cls.post,
            author=cls.user,
        )

        cls.fields_verbose_names = {
            "created": "Дата и время создания",
            "text": "Текст комментария",
            "post": "Пост, под которым опубликован комментарий",
            "author": "Автор комментария",
        }

        cls.fields_help_texts = {
            "text": "Введите текст будущего комментария",
        }

    def test_comment_object_name_is_first_symbols_preview(self):
        """У модели Comment корректно работает __str__."""

        self.assertEqual(
            first=self.comment.text[:COMMENT_PREVIEW_SYMBOLS],
            second=str(self.comment),
        )

    def test_comment_model_fields_verbose_names(self):
        """verbose_name в полях модели Comment совпадает с ожидаемым."""

        for value, expected in self.fields_verbose_names.items():
            with self.subTest(value=value):
                self.assertEqual(
                    first=self.comment._meta.get_field(
                        field_name=value
                    ).verbose_name,
                    second=expected,
                )

    def test_comment_model_fields_help_texts(self):
        """help_text в полях модели Comment совпадает с ожидаемым."""

        for value, expected in self.fields_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    first=self.comment._meta.get_field(
                        field_name=value
                    ).help_text,
                    second=expected,
                )


class FollowModelTest(TestCase):
    """Набор тестов для валидации модели Follow."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username="test_username",
        )
        cls.passion_of_user = User.objects.create_user(
            username="passion_of_test_username",
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.passion_of_user
        )

        cls.fields_verbose_names = {
            "created": "Дата и время создания",
            "user": "Подписчик контент-креатора",
            "author": "Контент-креатор",
        }

        cls.fields_help_texts = {
            "user": "Кто подписывается",
            "author": "На кого подписывается",
        }

    def test_follow_object_name_is_first_symbols_preview(self):
        """У модели Follow корректно работает __str__."""

        self.assertEqual(
            first=f"{self.user} follows {self.passion_of_user}",
            second=str(self.follow),
        )

    def test_follow_model_fields_verbose_names(self):
        """verbose_name в полях модели Follow совпадает с ожидаемым."""

        for value, expected in self.fields_verbose_names.items():
            with self.subTest(value=value):
                self.assertEqual(
                    first=self.follow._meta.get_field(
                        field_name=value
                    ).verbose_name,
                    second=expected,
                )

    def test_follow_model_fields_help_texts(self):
        """help_text в полях модели Follow совпадает с ожидаемым."""

        for value, expected in self.fields_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    first=self.follow._meta.get_field(
                        field_name=value
                    ).help_text,
                    second=expected,
                )

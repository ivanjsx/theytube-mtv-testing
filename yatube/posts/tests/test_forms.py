import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase, override_settings
from django.urls import reverse_lazy

from ..models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTests(TestCase):
    """Набор тестов для проверки форм пространства имён posts"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            slug="test_slug",
        )
        cls.user = User.objects.create_user(
            username="test_username",
        )
        cls.post = Post.objects.create(
            text="Текст тестового поста",
            author=cls.user,
            group=cls.group,
            image=SimpleUploadedFile(
                # green pixel
                name="green.gif",
                content_type="image/gif",
                content=(
                    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80"
                    b"\x00\x00\x00\xFF\x00\xFF\xFF\xFF\x21\xF9\x04"
                    b"\x00\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01"
                    b"\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B"
                ),
            ),
        )
        cls.comment = Comment.objects.create(
            text="Текст тестового комментария",
            post=cls.post,
            author=cls.user,
        )

        cls.post_form_fields = {
            # (field_name, expected_type, expected_initial, ),
            ("text", forms.fields.CharField, None, ),
            ("group", forms.models.ModelChoiceField, None, ),
            ("image", forms.fields.ImageField, None, ),
        }

        cls.comment_form_fields = {
            # (field_name, expected_type, expected_initial, ),
            ("text", forms.fields.CharField, None, ),
        }

        cls.test_form_data_new_post = {
            "text": ("Только что созданный пост, "
                     "на котором проверяется добавление в БД"),
            "group": cls.group.id,
            "image": SimpleUploadedFile(
                # red pixel
                name="red.gif",
                content_type="image/gif",
                content=(
                    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80"
                    b"\x00\x00\xFF\x00\x00\xFF\xFF\xFF\x21\xF9\x04"
                    b"\x00\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01"
                    b"\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B"
                ),
            ),
        }

        cls.test_form_data_edited_post = {
            "text": ("Только что отредактированный пост, "
                     "на котором проверяются изменения в БД"),
            "image": SimpleUploadedFile(
                # blue pixel
                name="blue.gif",
                content_type="image/gif",
                content=(
                    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80"
                    b"\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x21\xF9\x04"
                    b"\x00\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01"
                    b"\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B"
                ),
            ),
        }

        cls.test_form_data_new_comment = {
            "text": ("Только что созданный комментарий, "
                     "на котором проверяется добавление в БД"),
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(user=self.user)

    def tearDown(self):
        cache.clear()

    def test_post_create_form_shows_correct_fields(self):
        """
        У формы в post_create правильное количество полей.
        Их типы и начальные значения совпадают с ожидаемыми.
        """

        authorized_response = self.authorized_client.get(
            path=reverse_lazy(viewname="posts:post_create"), follow=False,
        )

        form_fields_count = len(authorized_response.context["form"].fields)
        self.assertEqual(
            first=len(self.post_form_fields),
            second=form_fields_count,
        )

        for name, expected_type, expected_initial in self.post_form_fields:
            with self.subTest(name=name):
                form_field = authorized_response.context["form"].fields[name]
                initial_value = form_field.initial
                self.assertIsInstance(
                    obj=form_field,
                    cls=expected_type,
                )
                self.assertEqual(
                    first=initial_value,
                    second=expected_initial,
                )

    def test_post_edit_form_shows_correct_fields(self):
        """
        У формы в post_edit правильное количество полей.
        Их типы и начальные значения совпадают с ожидаемыми.
        """

        authorized_response = self.authorized_client.get(
            path=reverse_lazy(
                viewname="posts:post_edit",
                kwargs={"post_id": self.post.id},
            ),
            follow=False,
        )

        form_fields_count = len(authorized_response.context["form"].fields)
        self.assertEqual(
            first=len(self.post_form_fields),
            second=form_fields_count,
        )

        for name, expected_type, expected_initial in self.post_form_fields:
            with self.subTest(name=name):
                form_field = authorized_response.context["form"].fields[name]
                initial_value = form_field.initial
                self.assertIsInstance(
                    obj=form_field,
                    cls=expected_type,
                )
                self.assertEqual(
                    first=initial_value,
                    second=expected_initial,
                )

    def test_post_detail_form_shows_correct_fields(self):
        """
        У формы в post_detail правильное количество полей.
        Их типы и начальные значения совпадают с ожидаемыми.
        """

        authorized_response = self.authorized_client.get(
            path=reverse_lazy(
                viewname="posts:post_detail",
                kwargs={"post_id": self.post.id},
            ), follow=False,
        )

        self.assertIsNotNone(authorized_response.context)
        form_fields_count = len(authorized_response.context["form"].fields)
        self.assertEqual(
            first=len(self.comment_form_fields),
            second=form_fields_count,
        )

        for name, expected_type, expected_initial in self.comment_form_fields:
            with self.subTest(name=name):
                form_field = authorized_response.context["form"].fields[name]
                initial_value = form_field.initial
                self.assertIsInstance(
                    obj=form_field,
                    cls=expected_type,
                )
                self.assertEqual(
                    first=initial_value,
                    second=expected_initial,
                )

    def test_created_post_shows_up_in_database(self):
        """Созданный пост появляется в базе данных."""

        initial_posts_count = Post.objects.count()

        self.authorized_client.post(
            path=reverse_lazy(viewname="posts:post_create"),
            data=self.test_form_data_new_post,
            follow=False,
        )

        self.assertTrue(
            Post.objects.filter(
                text=self.test_form_data_new_post["text"],
                group=self.test_form_data_new_post["group"],
            ).exists()
        )

        created_post = Post.objects.latest()

        self.assertEqual(
            first=Post.objects.count(),
            second=initial_posts_count + 1,
        )
        self.assertEqual(
            first=created_post.text,
            second=self.test_form_data_new_post["text"],
        )
        self.assertEqual(
            first=created_post.group.id,
            second=self.test_form_data_new_post["group"],
        )
        self.assertEqual(
            first=created_post.image.name,
            second=("posts/" + self.test_form_data_new_post["image"].name),
        )

    def test_created_comment_shows_up_in_database(self):
        """Созданный комментарий появляется в базе данных."""

        initial_comments_count = Comment.objects.count()

        self.authorized_client.post(
            path=reverse_lazy(
                viewname="posts:add_comment",
                kwargs={"post_id": self.post.id},
            ),
            data=self.test_form_data_new_comment,
            follow=False,
        )

        self.assertTrue(
            Comment.objects.filter(
                text=self.test_form_data_new_comment["text"],
            ).exists()
        )

        created_comment = Comment.objects.latest()

        self.assertEqual(
            first=Comment.objects.count(),
            second=initial_comments_count + 1,
        )
        self.assertEqual(
            first=created_comment.text,
            second=self.test_form_data_new_comment["text"],
        )

    def test_edited_post_changes_in_database(self):
        """Отредактированный пост меняется в базе данных."""

        initial_post = get_object_or_404(klass=Post, id=self.post.id)
        initial_posts_count = Post.objects.count()

        self.authorized_client.post(
            path=reverse_lazy(
                viewname="posts:post_edit",
                kwargs={"post_id": self.post.id},
            ),
            data=self.test_form_data_edited_post,
            follow=True,
        )

        changed_post = get_object_or_404(klass=Post, id=self.post.id)

        self.assertEqual(
            first=Post.objects.count(),
            second=initial_posts_count,
        )

        self.assertEqual(
            first=initial_post.text,
            second=self.post.text,
        )
        self.assertEqual(
            first=initial_post.group,
            second=self.post.group,
        )
        self.assertEqual(
            first=initial_post.image,
            second=self.post.image,
        )

        self.assertEqual(
            first=changed_post.text,
            second=self.test_form_data_edited_post["text"],
        )
        self.assertEqual(
            first=changed_post.group,
            second=self.test_form_data_edited_post.get("group"),
        )
        self.assertEqual(
            first=changed_post.image.name,
            second=(
                "posts/" + self.test_form_data_edited_post.get(
                    "image"
                ).name
            ),
        )

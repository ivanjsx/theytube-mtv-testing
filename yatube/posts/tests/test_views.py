import datetime
import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse_lazy

from ..forms import CommentForm, PostForm
from ..models import Comment, Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    """Набор тестов для проверки вью-функций пространства имён posts"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            slug="test_slug",
        )
        cls.other_group = Group.objects.create(
            slug="other_test_slug",
        )
        cls.user = User.objects.create_user(
            username="test_username",
        )
        cls.other_user = User.objects.create_user(
            username="other_test_username",
        )
        cls.passion_of_user = User.objects.create_user(
            username="passion_of_test_username",
        )

        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.passion_of_user,
        )

        cls.post_1960 = Post.objects.create(
            created=datetime.date(1960, 1, 1),
            text="Тестовый пост 1960 года",
            author=cls.user,
            group=cls.group,
        )
        cls.post_1970 = Post.objects.create(
            created=datetime.date(1970, 1, 1),
            text="Тестовый пост 1970 года",
            author=cls.other_user,
            group=cls.group,
        )
        cls.post_1980 = Post.objects.create(
            created=datetime.date(1980, 1, 1),
            text="Тестовый пост 1980 года",
            author=cls.user,
            group=cls.other_group,
        )
        cls.post_1990 = Post.objects.create(
            created=datetime.date(1990, 1, 1),
            text="Тестовый пост 1990 года",
            author=cls.other_user,
            group=cls.other_group,
        )
        cls.post_2000 = Post.objects.create(
            created=datetime.date(2000, 1, 1),
            text="Тестовый пост 2000 года",
            author=cls.passion_of_user,
        )
        cls.post_2010 = Post.objects.create(
            created=datetime.date(2010, 1, 1),
            text="Тестовый пост 2000 года",
            author=cls.passion_of_user,
        )

        cls.target_posts_sequence_index = {
            0: cls.post_2010,
            1: cls.post_2000,
            2: cls.post_1990,
            3: cls.post_1980,
            4: cls.post_1970,
            5: cls.post_1960,
        }
        cls.target_posts_sequence_follow_index = {
            0: cls.post_2010,
            1: cls.post_2000,
        }
        cls.target_posts_sequence_user = {
            0: cls.post_1980,
            1: cls.post_1960,
        }
        cls.target_posts_sequence_other_user = {
            0: cls.post_1990,
            1: cls.post_1970,
        }
        cls.target_posts_sequence_group = {
            0: cls.post_1970,
            1: cls.post_1960,
        }
        cls.target_posts_sequence_other_group = {
            0: cls.post_1990,
            1: cls.post_1980,
        }
        cls.target_post_objects_detail = {
            cls.post_1960.id: cls.post_1960,
            cls.post_1970.id: cls.post_1970,
            cls.post_1980.id: cls.post_1980,
            cls.post_1990.id: cls.post_1990,
            cls.post_2000.id: cls.post_2000,
            cls.post_2010.id: cls.post_2010,
        }

        cls.test_form_data_new_comment = {
            "text": ("Только что созданный комментарий, "
                     "на котором проверяется редирект "
                     "и появление на странице поста"),
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(user=self.user)

        self.test_form_data_new_post = {
            "text": ("Только что созданный пост, "
                     "на котором проверяется редирект "
                     "и попадание на страницы"),
            "group": self.group.id,
            "image": SimpleUploadedFile(
                # pink pixel
                name="pink.gif",
                content_type="image/gif",
                content=(
                    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80"
                    b"\x00\x00\xFF\xC0\xCB\xFF\xFF\xFF\x21\xF9\x04"
                    b"\x00\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01"
                    b"\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B"
                ),
            ),
        }

        self.test_form_data_edited_post = {
            "text": ("Только что отредактированный пост 1960 года, "
                     "на котором проверяется редирект"),
            "image": SimpleUploadedFile(
                # purple pixel
                name="purple.gif",
                content_type="image/gif",
                content=(
                    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80"
                    b"\x00\x00\x80\x00\x80\xFF\xFF\xFF\x21\xF9\x04"
                    b"\x00\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01"
                    b"\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B"
                ),
            ),
        }

    def tearDown(self):
        cache.clear()

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""

        guest_response = self.guest_client.get(
            path=reverse_lazy(viewname="posts:index"), follow=False,
        )

        self.assertEqual(
            first=len(guest_response.context["page_obj"]),
            second=len(self.target_posts_sequence_index),
        )

        for number, expected in self.target_posts_sequence_index.items():
            with self.subTest(number=number):
                self.assertEqual(
                    first=guest_response.context["page_obj"][number],
                    second=expected,
                )

    def test_follow_index_page_show_correct_context(self):
        """Шаблон follow_index сформирован с правильным контекстом."""

        authorized_response = self.authorized_client.get(
            path=reverse_lazy(viewname="posts:index"), follow=False,
        )

        self.assertEqual(
            first=len(authorized_response.context["page_obj"]),
            second=len(self.target_posts_sequence_index),
        )

        for number, expected in self.target_posts_sequence_index.items():
            with self.subTest(number=number):
                self.assertEqual(
                    first=authorized_response.context["page_obj"][number],
                    second=expected,
                )

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""

        guest_response = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:group_list",
                kwargs={"slug": self.group.slug},
            ),
            follow=False,
        )

        self.assertEqual(
            first=guest_response.context["group"],
            second=self.group,
        )
        self.assertEqual(
            first=len(guest_response.context["page_obj"]),
            second=len(self.target_posts_sequence_group),
        )

        for number, expected in self.target_posts_sequence_group.items():
            with self.subTest(number=number):
                self.assertEqual(
                    first=guest_response.context["page_obj"][number],
                    second=expected,
                )

        guest_response = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:group_list",
                kwargs={"slug": self.other_group.slug},
            ),
            follow=False,
        )

        self.assertEqual(
            first=guest_response.context["group"],
            second=self.other_group,
        )
        self.assertEqual(
            first=len(guest_response.context["page_obj"]),
            second=len(self.target_posts_sequence_other_group),
        )

        for number, expected in self.target_posts_sequence_other_group.items():
            with self.subTest(number=number):
                self.assertEqual(
                    first=guest_response.context["page_obj"][number],
                    second=expected,
                )

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""

        guest_response = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": self.user.username},
            ),
            follow=False,
        )

        self.assertEqual(
            first=guest_response.context["author"],
            second=self.user,
        )
        self.assertEqual(
            first=len(guest_response.context["page_obj"]),
            second=len(self.target_posts_sequence_user),
        )

        for number, expected in self.target_posts_sequence_user.items():
            with self.subTest(number=number):
                self.assertEqual(
                    first=guest_response.context["page_obj"][number],
                    second=expected,
                )

        guest_response = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": self.other_user.username},
            ),
            follow=False,
        )

        self.assertEqual(
            first=guest_response.context["author"],
            second=self.other_user,
        )
        self.assertEqual(
            first=len(guest_response.context["page_obj"]),
            second=len(self.target_posts_sequence_other_user),
        )

        for number, expected in self.target_posts_sequence_other_user.items():
            with self.subTest(number=number):
                self.assertEqual(
                    first=guest_response.context["page_obj"][number],
                    second=expected,
                )

    def test_profile_page_show_correct_follow_button(self):
        """В шаблон profile передаётся правильное значение following."""

        guest_response = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": self.other_user.username},
            ),
            follow=False,
        )
        self.assertEqual(
            first=guest_response.context["following"],
            second=False,
        )

        guest_response = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": self.passion_of_user.username},
            ),
            follow=False,
        )
        self.assertEqual(
            first=guest_response.context["following"],
            second=False,
        )

        authorized_response = self.authorized_client.get(
            path=reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": self.other_user.username},
            ),
            follow=False,
        )
        self.assertEqual(
            first=authorized_response.context["following"],
            second=False,
        )

        authorized_response = self.authorized_client.get(
            path=reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": self.passion_of_user.username},
            ),
            follow=False,
        )
        self.assertEqual(
            first=authorized_response.context["following"],
            second=True,
        )

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""

        for post_id, expected in self.target_post_objects_detail.items():
            with self.subTest(post_id=post_id):
                guest_response = self.guest_client.get(
                    path=reverse_lazy(
                        viewname="posts:post_detail",
                        kwargs={"post_id": post_id},
                    ),
                    follow=False,
                )
                self.assertEqual(
                    first=guest_response.context["post"],
                    second=expected,
                )
                self.assertIsInstance(
                    obj=guest_response.context["form"],
                    cls=CommentForm,
                )

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""

        authorized_response = self.authorized_client.get(
            path=reverse_lazy(viewname="posts:post_create"),
            follow=False,
        )
        self.assertIsInstance(
            obj=authorized_response.context["form"],
            cls=PostForm,
        )

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""

        authorized_response = self.authorized_client.get(
            path=reverse_lazy(
                viewname="posts:post_edit",
                kwargs={"post_id": self.post_1960.id},
            ),
            follow=False,
        )
        self.assertIsInstance(
            obj=authorized_response.context["form"],
            cls=PostForm,
        )

    def test_redirect_after_post_creation(self):
        """После создания поста происходит редирект на страницу автора."""

        authorized_response = self.authorized_client.post(
            path=reverse_lazy(viewname="posts:post_create"),
            data=self.test_form_data_new_post,
            follow=False,
        )
        self.assertRedirects(
            response=authorized_response,
            expected_url=reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": self.user.username},
            ),
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )

    def test_created_post_shows_up_on_right_pages(self):
        """
        Созданный пост появляется на странице автора, группы, на Главной.
        Появляется страница, которая ему посвящена.
        """

        authorized_response = self.authorized_client.post(
            path=reverse_lazy(viewname="posts:post_create"),
            data=self.test_form_data_new_post,
            follow=True,
        )

        self.assertTrue(
            Post.objects.filter(
                text=self.test_form_data_new_post["text"],
            ).exists()
        )

        created_post = Post.objects.latest()

        self.assertEqual(
            first=authorized_response.context["page_obj"][0],
            second=created_post,
        )

        guest_response = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:post_detail",
                kwargs={"post_id": created_post.id},
            ),
            follow=False,
        )
        self.assertEqual(
            first=guest_response.status_code,
            second=HTTPStatus.OK,
        )
        self.assertEqual(
            first=guest_response.context["post"],
            second=created_post,
        )

        guest_response = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:group_list",
                kwargs={"slug": self.group.slug},
            ),
            follow=False,
        )
        self.assertEqual(
            first=guest_response.context["page_obj"][0],
            second=created_post,
        )

        guest_response = self.guest_client.get(
            path=reverse_lazy(viewname="posts:index"),
            follow=False,
        )
        self.assertEqual(
            first=guest_response.context["page_obj"][0],
            second=created_post,
        )

    def test_created_post_doesnt_show_up_on_wrong_pages(self):
        """Созданный пост не появляется на странице других авторов и групп."""

        self.authorized_client.post(
            path=reverse_lazy(viewname="posts:post_create"),
            data=self.test_form_data_new_post,
            follow=False,
        )

        created_post = Post.objects.latest()

        guest_response = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": self.other_user.username},
            ),
            follow=False,
        )
        self.assertNotEqual(
            first=guest_response.context["page_obj"][0],
            second=created_post,
        )

        guest_response = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:group_list",
                kwargs={"slug": self.other_group.slug},
            ),
            follow=False,
        )
        self.assertNotEqual(
            first=guest_response.context["page_obj"][0],
            second=created_post,
        )

    def test_redirect_after_post_edited(self):
        """После редактирования поста происходит редирект на страницу поста."""

        authorized_response = self.authorized_client.post(
            path=reverse_lazy(
                viewname="posts:post_edit",
                kwargs={"post_id": self.post_1960.id},
            ),
            data=self.test_form_data_edited_post,
            follow=False,
        )

        self.assertRedirects(
            response=authorized_response,
            expected_url=reverse_lazy(
                viewname="posts:post_detail",
                kwargs={"post_id": self.post_1960.id},
            ),
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )

    def test_redirect_after_comment_creation(self):
        """После создания комментария происходит редирект на страницу поста."""

        authorized_response = self.authorized_client.post(
            path=reverse_lazy(
                viewname="posts:add_comment",
                kwargs={"post_id": self.post_1960.id},
            ),
            data=self.test_form_data_new_comment,
            follow=False,
        )
        self.assertRedirects(
            response=authorized_response,
            expected_url=reverse_lazy(
                viewname="posts:post_detail",
                kwargs={"post_id": self.post_1960.id},
            ),
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )

    def test_created_comment_shows_up_on_post_page(self):
        """Созданный комментарий появляется на странице поста."""

        authorized_response = self.authorized_client.post(
            path=reverse_lazy(
                viewname="posts:add_comment",
                kwargs={"post_id": self.post_1960.id},
            ),
            data=self.test_form_data_new_comment,
            follow=True,
        )

        self.assertTrue(
            Comment.objects.filter(
                text=self.test_form_data_new_comment["text"],
            ).exists()
        )

        created_comment = Comment.objects.latest()

        self.assertEqual(
            first=authorized_response.status_code,
            second=HTTPStatus.OK,
        )
        self.assertEqual(
            first=authorized_response.context["post"].comments.all()[0],
            second=created_comment,
        )

    def test_successfully_create_new_follow(self):
        """Подписка успешно создаётся при запросе по адресу."""

        initial_follows_count = Follow.objects.count()

        authorized_response = self.authorized_client.get(
            path=reverse_lazy(
                viewname="posts:profile_follow",
                kwargs={"username": self.other_user.username},
            ),
            follow=True,
        )
        self.assertEqual(
            first=Follow.objects.count(),
            second=initial_follows_count + 1,
        )
        self.assertEqual(
            first=authorized_response.status_code,
            second=HTTPStatus.OK,
        )

    def test_successfully_delete_follow(self):
        """Подписка успешно удаляется при запросе по адресу."""

        initial_follows_count = Follow.objects.count()

        authorized_response = self.authorized_client.get(
            path=reverse_lazy(
                viewname="posts:profile_unfollow",
                kwargs={"username": self.passion_of_user.username},
            ),
            follow=True,
        )
        self.assertEqual(
            first=Follow.objects.count(),
            second=initial_follows_count - 1,
        )
        self.assertEqual(
            first=authorized_response.status_code,
            second=HTTPStatus.OK,
        )

    def test_cannot_follow_myself(self):
        """Нельзя подписаться на себя, но ничего при этом не ломается."""

        initial_follows_count = Follow.objects.count()

        authorized_response = self.authorized_client.get(
            path=reverse_lazy(
                viewname="posts:profile_follow",
                kwargs={"username": self.user.username},
            ),
            follow=True,
        )
        self.assertEqual(
            first=Follow.objects.count(),
            second=initial_follows_count,
        )
        self.assertEqual(
            first=authorized_response.status_code,
            second=HTTPStatus.OK,
        )

    def test_cannot_follow_already_following(self):
        """
        Нельзя подписаться на того, на кого уже подписан,
        но ничего при этом не ломается.
        """

        initial_follows_count = Follow.objects.count()

        authorized_response = self.authorized_client.get(
            path=reverse_lazy(
                viewname="posts:profile_follow",
                kwargs={"username": self.passion_of_user.username},
            ),
            follow=True,
        )
        self.assertEqual(
            first=Follow.objects.count(),
            second=initial_follows_count,
        )
        self.assertEqual(
            first=authorized_response.status_code,
            second=HTTPStatus.OK,
        )

    def test_cannot_unfollow_who_you_dont_follow(self):
        """
        Нельзя отписаться от того, на кого и не был подписан,
        но ничего при этом не ломается.
        """

        initial_follows_count = Follow.objects.count()

        authorized_response = self.authorized_client.get(
            path=reverse_lazy(
                viewname="posts:profile_unfollow",
                kwargs={"username": self.other_user.username},
            ),
            follow=True,
        )
        self.assertEqual(
            first=Follow.objects.count(),
            second=initial_follows_count,
        )
        self.assertEqual(
            first=authorized_response.status_code,
            second=HTTPStatus.OK,
        )

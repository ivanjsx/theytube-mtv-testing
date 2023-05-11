import time
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse_lazy

from ..constants import CACHE_TIMEOUT_SECONDS
from ..models import Group, Post

User = get_user_model()


class PostsCacheTests(TestCase):
    """Набор тестов для проверки кэширования страниц пространства имён posts"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username="test_username",
        )
        cls.group = Group.objects.create(
            id=1,
            slug="test_slug",
        )
        cls.post = Post.objects.create(
            id=1,
            text="Тестовый текст тестового поста",
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(user=self.user)

    def test_index_page_caches(self):
        """Шаблон index использует кэш с обозначенными параметрами."""

        initial_response = self.guest_client.get(
            path=reverse_lazy(viewname="posts:index"), follow=False,
        )
        self.assertEqual(
            first=initial_response.status_code,
            second=HTTPStatus.OK,
        )
        self.assertEqual(
            first=len(initial_response.context["page_obj"]),
            second=1,
        )

        Post.objects.get(id=1).delete()

        response_after_post_deletion = self.guest_client.get(
            path=reverse_lazy(viewname="posts:index"), follow=False,
        )
        self.assertEqual(
            first=response_after_post_deletion.status_code,
            second=HTTPStatus.OK,
        )
        self.assertIsNone(
            obj=response_after_post_deletion.context,
        )
        self.assertHTMLEqual(
            html1=initial_response.content.decode("utf-8"),
            html2=response_after_post_deletion.content.decode("utf-8"),
        )

        time.sleep(CACHE_TIMEOUT_SECONDS + 1)

        response_after_cache_clearance = self.guest_client.get(
            path=reverse_lazy(viewname="posts:index"), follow=False,
        )
        self.assertEqual(
            first=response_after_cache_clearance.status_code,
            second=HTTPStatus.OK,
        )
        self.assertEqual(
            first=len(response_after_cache_clearance.context["page_obj"]),
            second=0,
        )

    def test_group_page_caches(self):
        """Шаблон group_list использует кэш с обозначенными параметрами."""

        initial_response = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:group_list",
                kwargs={"slug": self.group.slug}
            ), follow=False,
        )
        self.assertEqual(
            first=initial_response.status_code,
            second=HTTPStatus.OK,
        )
        self.assertEqual(
            first=len(initial_response.context["page_obj"]),
            second=1,
        )

        Post.objects.get(id=1).delete()

        response_after_post_deletion = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:group_list",
                kwargs={"slug": self.group.slug}
            ), follow=False,
        )
        self.assertEqual(
            first=response_after_post_deletion.status_code,
            second=HTTPStatus.OK,
        )
        self.assertIsNone(
            obj=response_after_post_deletion.context,
        )
        self.assertHTMLEqual(
            html1=initial_response.content.decode("utf-8"),
            html2=response_after_post_deletion.content.decode("utf-8"),
        )

        time.sleep(CACHE_TIMEOUT_SECONDS + 1)

        response_after_cache_clearance = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:group_list",
                kwargs={"slug": self.group.slug}
            ), follow=False,
        )
        self.assertEqual(
            first=response_after_cache_clearance.status_code,
            second=HTTPStatus.OK,
        )
        self.assertEqual(
            first=len(response_after_cache_clearance.context["page_obj"]),
            second=0,
        )

        Group.objects.get(id=1).delete()

        response_after_group_deletion = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:group_list",
                kwargs={"slug": self.group.slug}
            ), follow=False,
        )
        self.assertEqual(
            first=response_after_group_deletion.status_code,
            second=HTTPStatus.OK,
        )
        self.assertIsNone(
            obj=response_after_group_deletion.context,
        )
        self.assertHTMLEqual(
            html1=response_after_cache_clearance.content.decode("utf-8"),
            html2=response_after_group_deletion.content.decode("utf-8"),
        )

        time.sleep(CACHE_TIMEOUT_SECONDS + 1)

        response_after_cache_clearance = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:group_list",
                kwargs={"slug": self.group.slug}
            ), follow=False,
        )
        self.assertEqual(
            first=response_after_cache_clearance.status_code,
            second=HTTPStatus.NOT_FOUND,
        )

    def test_post_detail_page_caches(self):
        """Шаблон post_detail использует кэш с обозначенными параметрами."""

        post_id = self.post.id

        initial_response = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:post_detail",
                kwargs={"post_id": post_id},
            ), follow=False,
        )
        self.assertEqual(
            first=initial_response.status_code,
            second=HTTPStatus.OK,
        )
        self.assertEqual(
            first=initial_response.context["post"],
            second=self.post,
        )

        Post.objects.get(id=1).delete()

        response_after_post_deletion = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:post_detail",
                kwargs={"post_id": post_id},
            ), follow=False,
        )
        self.assertEqual(
            first=response_after_post_deletion.status_code,
            second=HTTPStatus.OK,
        )
        self.assertIsNone(
            obj=response_after_post_deletion.context,
        )
        self.assertHTMLEqual(
            html1=initial_response.content.decode("utf-8"),
            html2=response_after_post_deletion.content.decode("utf-8"),
        )

        time.sleep(CACHE_TIMEOUT_SECONDS + 1)

        response_after_cache_clearance = self.guest_client.get(
            path=reverse_lazy(
                viewname="posts:post_detail",
                kwargs={"post_id": post_id},
            ), follow=False,
        )
        self.assertEqual(
            first=response_after_cache_clearance.status_code,
            second=HTTPStatus.NOT_FOUND,
        )

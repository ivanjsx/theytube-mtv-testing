from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse_lazy

from ..models import Follow, Group, Post

User = get_user_model()


class PostsCacheTests(TestCase):
    """Набор тестов для проверки кэширования страниц пространства имён posts"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_username",
        )
        self.passion_of_user = User.objects.create_user(
            username="passion_of_test_username",
        )
        self.follow = Follow.objects.create(
            user=self.user,
            author=self.passion_of_user,
        )
        self.group = Group.objects.create(
            id=1,
            slug="test_slug",
        )

        self.own_post = Post.objects.create(
            # id=1,    # задаём явно, иначе не сработает .delete()
            text="Тестовый текст тестового поста",
            author=self.user,
            group=self.group,
        )
        self.ones_post = Post.objects.create(
            # id=2,    # задаём явно, иначе не сработает .delete()
            text="Тестовый текст тестового поста",
            author=self.passion_of_user,
        )

        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(user=self.user)

    def tearDown(self):
        cache.clear()

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
            second=2,
        )

        self.own_post.delete()

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

        cache.clear()

        response_after_cache_clearance = self.guest_client.get(
            path=reverse_lazy(viewname="posts:index"), follow=False,
        )
        self.assertEqual(
            first=response_after_cache_clearance.status_code,
            second=HTTPStatus.OK,
        )
        self.assertEqual(
            first=len(response_after_cache_clearance.context["page_obj"]),
            second=1,
        )

    # def test_group_page_caches(self):
    #     """Шаблон group_list использует кэш с обозначенными параметрами."""

    #     group_slug = self.group.slug

    #     initial_response = self.guest_client.get(
    #         path=reverse_lazy(
    #             viewname="posts:group_list",
    #             kwargs={"slug": group_slug}
    #         ), follow=False,
    #     )
    #     self.assertEqual(
    #         first=initial_response.status_code,
    #         second=HTTPStatus.OK,
    #     )
    #     self.assertEqual(
    #         first=len(initial_response.context["page_obj"]),
    #         second=1,
    #     )

    #     self.own_post.delete()

    #     response_after_post_deletion = self.guest_client.get(
    #         path=reverse_lazy(
    #             viewname="posts:group_list",
    #             kwargs={"slug": group_slug}
    #         ), follow=False,
    #     )
    #     self.assertEqual(
    #         first=response_after_post_deletion.status_code,
    #         second=HTTPStatus.OK,
    #     )
    #     self.assertIsNone(
    #         obj=response_after_post_deletion.context,
    #     )
    #     self.assertHTMLEqual(
    #         html1=initial_response.content.decode("utf-8"),
    #         html2=response_after_post_deletion.content.decode("utf-8"),
    #     )

    #     cache.clear()

    #     response_after_cache_clearance = self.guest_client.get(
    #         path=reverse_lazy(
    #             viewname="posts:group_list",
    #             kwargs={"slug": group_slug}
    #         ), follow=False,
    #     )
    #     self.assertEqual(
    #         first=response_after_cache_clearance.status_code,
    #         second=HTTPStatus.OK,
    #     )
    #     self.assertEqual(
    #         first=len(response_after_cache_clearance.context["page_obj"]),
    #         second=0,
    #     )

    #     self.group.delete()

    #     response_after_group_deletion = self.guest_client.get(
    #         path=reverse_lazy(
    #             viewname="posts:group_list",
    #             kwargs={"slug": group_slug}
    #         ), follow=False,
    #     )
    #     self.assertEqual(
    #         first=response_after_group_deletion.status_code,
    #         second=HTTPStatus.OK,
    #     )
    #     self.assertIsNone(
    #         obj=response_after_group_deletion.context,
    #     )
    #     self.assertHTMLEqual(
    #         html1=response_after_cache_clearance.content.decode("utf-8"),
    #         html2=response_after_group_deletion.content.decode("utf-8"),
    #     )

    #     cache.clear()

    #     response_after_cache_clearance = self.guest_client.get(
    #         path=reverse_lazy(
    #             viewname="posts:group_list",
    #             kwargs={"slug": group_slug}
    #         ), follow=False,
    #     )
    #     self.assertEqual(
    #         first=response_after_cache_clearance.status_code,
    #         second=HTTPStatus.NOT_FOUND,
    #     )

    # def test_profile_page_caches(self):
    #     """Шаблон profile использует кэш с обозначенными параметрами."""

    #     username = self.user.username

    #     initial_response = self.guest_client.get(
    #         path=reverse_lazy(
    #             viewname="posts:profile",
    #             kwargs={"username": username}
    #         ), follow=False,
    #     )
    #     self.assertEqual(
    #         first=initial_response.status_code,
    #         second=HTTPStatus.OK,
    #     )
    #     self.assertEqual(
    #         first=len(initial_response.context["page_obj"]),
    #         second=1,
    #     )

    #     self.own_post.delete()

    #     response_after_post_deletion = self.guest_client.get(
    #         path=reverse_lazy(
    #             viewname="posts:profile",
    #             kwargs={"username": username}
    #         ), follow=False,
    #     )
    #     self.assertEqual(
    #         first=response_after_post_deletion.status_code,
    #         second=HTTPStatus.OK,
    #     )
    #     self.assertIsNone(
    #         obj=response_after_post_deletion.context,
    #     )
    #     self.assertHTMLEqual(
    #         html1=initial_response.content.decode("utf-8"),
    #         html2=response_after_post_deletion.content.decode("utf-8"),
    #     )

    #     cache.clear()

    #     response_after_cache_clearance = self.guest_client.get(
    #         path=reverse_lazy(
    #             viewname="posts:profile",
    #             kwargs={"username": username}
    #         ), follow=False,
    #     )
    #     self.assertEqual(
    #         first=response_after_cache_clearance.status_code,
    #         second=HTTPStatus.OK,
    #     )
    #     self.assertEqual(
    #         first=len(response_after_cache_clearance.context["page_obj"]),
    #         second=0,
    #     )

    #     self.user.delete()

    #     response_after_group_deletion = self.guest_client.get(
    #         path=reverse_lazy(
    #             viewname="posts:profile",
    #             kwargs={"username": username}
    #         ), follow=False,
    #     )
    #     self.assertEqual(
    #         first=response_after_group_deletion.status_code,
    #         second=HTTPStatus.OK,
    #     )
    #     self.assertIsNone(
    #         obj=response_after_group_deletion.context,
    #     )
    #     self.assertHTMLEqual(
    #         html1=response_after_cache_clearance.content.decode("utf-8"),
    #         html2=response_after_group_deletion.content.decode("utf-8"),
    #     )

    #     cache.clear()

    #     response_after_cache_clearance = self.guest_client.get(
    #         path=reverse_lazy(
    #             viewname="posts:profile",
    #             kwargs={"username": username}
    #         ), follow=False,
    #     )
    #     self.assertEqual(
    #         first=response_after_cache_clearance.status_code,
    #         second=HTTPStatus.NOT_FOUND,
    #     )

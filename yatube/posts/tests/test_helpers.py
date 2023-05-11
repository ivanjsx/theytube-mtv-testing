from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse_lazy

from ..constants import (POSTS_PER_PAGE,
                         TESTS_ALL_POSTS_TOTAL_PAGES,
                         TESTS_GROUP_POSTS_TOTAL_PAGES,
                         TESTS_OTHER_GROUP_POSTS_TOTAL_PAGES,
                         TESTS_OTHER_USER_POSTS_TOTAL_PAGES,
                         TESTS_POSTS_PER_PAGE_MULTIPLIER,
                         TESTS_USER_POSTS_TOTAL_PAGES)
from ..models import Group, Post

User = get_user_model()


class PaginationTests(TestCase):
    """Набор тестов для проверки корректности работы пагинатора"""

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

        # создаём посты так, чтобы одновременно выполнялись 3 условия:
        # 1. на страницах двух разных юзеров было разное количество страниц
        # 2. на страницах двух разных групп было разное количество страниц
        # 3. и ни одно из этих чисел не совпадало с кол-вом страниц на Главной

        cls.posts = Post.objects.bulk_create(
            objs=[
                Post(author=cls.user, group=cls.group),
                Post(author=cls.user, group=cls.other_group),
                Post(author=cls.other_user, group=cls.other_group),
            ] * int(
                POSTS_PER_PAGE * TESTS_POSTS_PER_PAGE_MULTIPLIER
            ),
        )

    def setUp(self):
        self.guest_client = Client()

    def test_ensure_first_page_is_not_the_only_one(self):
        """
        Первая страница каждого раздела не единственная.
        И, соответственно, полностью заполнена.
        """

        objects_count_min_values = [
            (
                "all_posts",
                Post.objects.count(),
                POSTS_PER_PAGE,
            ),
            (
                "user_posts",
                self.user.posts.count(),
                POSTS_PER_PAGE,
            ),
            (
                "group_posts",
                self.group.posts.count(),
                POSTS_PER_PAGE,
            ),
            (
                "other_user_posts",
                self.other_user.posts.count(),
                POSTS_PER_PAGE,
            ),
            (
                "other_group_posts",
                self.other_group.posts.count(),
                POSTS_PER_PAGE,
            ),
        ]

        for objects, count, min_value in objects_count_min_values:
            with self.subTest(objects=objects):
                self.assertGreater(
                    a=count,
                    b=min_value,
                )

    def test_ensure_second_page_is_the_last_one_and_not_full(self):
        """Последняя страница каждого раздела заполнена не полностью"""

        objects_count_max_values = [
            (
                "all_posts",
                Post.objects.count(),
                POSTS_PER_PAGE * TESTS_ALL_POSTS_TOTAL_PAGES,
            ),
            (
                "user_posts",
                self.user.posts.count(),
                POSTS_PER_PAGE * TESTS_USER_POSTS_TOTAL_PAGES,
            ),
            (
                "group_posts",
                self.group.posts.count(),
                POSTS_PER_PAGE * TESTS_GROUP_POSTS_TOTAL_PAGES,
            ),
            (
                "other_user_posts",
                self.other_user.posts.count(),
                POSTS_PER_PAGE * TESTS_OTHER_USER_POSTS_TOTAL_PAGES,
            ),
            (
                "other_group_posts",
                self.other_group.posts.count(),
                POSTS_PER_PAGE * TESTS_OTHER_GROUP_POSTS_TOTAL_PAGES,
            ),
        ]

        for objects, count, max_value in objects_count_max_values:
            with self.subTest(objects=objects):
                self.assertLess(
                    a=count,
                    b=max_value,
                )

    def test_pages_contain_expected_records_amount(self):
        """
        Тестируется корректность работы паджинатора.
        Проверяется, что страницы содержат ожидаемое количество объектов.
        """

        path_objects_count = {
            reverse_lazy(
                viewname="posts:index"
            ) + "?page=1": POSTS_PER_PAGE,
            reverse_lazy(
                viewname="posts:index"
            ) + "?page=2": POSTS_PER_PAGE,
            reverse_lazy(
                viewname="posts:index"
            ) + "?page=3": POSTS_PER_PAGE,
            reverse_lazy(
                viewname="posts:index"
            ) + "?page=4": (
                Post.objects.count()
                - POSTS_PER_PAGE * (TESTS_ALL_POSTS_TOTAL_PAGES - 1)
            ),

            reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": self.user.username},
            ) + "?page=1": POSTS_PER_PAGE,
            reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": self.user.username},
            ) + "?page=2": POSTS_PER_PAGE,
            reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": self.user.username},
            ) + "?page=3": (
                self.user.posts.count()
                - POSTS_PER_PAGE * (TESTS_USER_POSTS_TOTAL_PAGES - 1)
            ),

            reverse_lazy(
                viewname="posts:group_list",
                kwargs={"slug": self.group.slug},
            ) + "?page=1": POSTS_PER_PAGE,
            reverse_lazy(
                viewname="posts:group_list",
                kwargs={"slug": self.group.slug},
            ) + "?page=2": (
                self.group.posts.count()
                - POSTS_PER_PAGE * (TESTS_GROUP_POSTS_TOTAL_PAGES - 1)
            ),

            reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": self.other_user.username},
            ) + "?page=1": POSTS_PER_PAGE,
            reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": self.other_user.username},
            ) + "?page=2": (
                self.other_user.posts.count()
                - POSTS_PER_PAGE * (TESTS_OTHER_USER_POSTS_TOTAL_PAGES - 1)
            ),

            reverse_lazy(
                viewname="posts:group_list",
                kwargs={"slug": self.other_group.slug},
            ) + "?page=1": POSTS_PER_PAGE,
            reverse_lazy(
                viewname="posts:group_list",
                kwargs={"slug": self.other_group.slug},
            ) + "?page=2": POSTS_PER_PAGE,
            reverse_lazy(
                viewname="posts:group_list",
                kwargs={"slug": self.other_group.slug},
            ) + "?page=3": (
                self.other_group.posts.count()
                - POSTS_PER_PAGE * (TESTS_OTHER_GROUP_POSTS_TOTAL_PAGES - 1)
            ),
        }

        for path, expected in path_objects_count.items():
            with self.subTest(path=path):
                guest_response = self.guest_client.get(
                    path=path, follow=False,
                )
                self.assertEqual(
                    first=len(guest_response.context["page_obj"]),
                    second=expected,
                )

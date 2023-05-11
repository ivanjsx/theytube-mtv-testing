from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse_lazy

from ..models import Follow, Group, Post

User = get_user_model()


class PostsURLsTests(TestCase):
    """Набор тестов для проверки адресов пространства имён posts"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username="test_username",
        )
        cls.other_user = User.objects.create_user(
            username="other_username",
        )
        cls.passion_of_user = User.objects.create_user(
            username="passion_of_test_username",
        )

        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.passion_of_user,
        )

        cls.own_post = Post.objects.create(
            author=cls.user,
        )
        cls.ones_post = Post.objects.create(
            author=cls.other_user,
        )

        cls.group = Group.objects.create(
            slug="test_slug",
        )

        # !!!! все адреса, отдающие одинаковые конечные статусы ответа
        # !!!! вне зависимости от статуса авторизации пользователя.
        # поведение словаря ниже описывает ответы для всех типов клиентов.
        cls.public_paths_status_codes = {
            "/": HTTPStatus.OK,
            "/group/": HTTPStatus.NOT_FOUND,
            f"/group/{cls.group.slug}/": HTTPStatus.OK,
            "/group/non_existing_slug/": HTTPStatus.NOT_FOUND,
            "/profile/": HTTPStatus.NOT_FOUND,
            f"/profile/{cls.user.username}/": HTTPStatus.OK,
            f"/profile/{cls.other_user.username}/": HTTPStatus.OK,
            "/profile/non_existing_username/": HTTPStatus.NOT_FOUND,
            "/posts/": HTTPStatus.NOT_FOUND,
            f"/posts/{cls.own_post.id}/": HTTPStatus.OK,
            f"/posts/{cls.ones_post.id}/": HTTPStatus.OK,
            "/posts/69420/": HTTPStatus.NOT_FOUND,
        }

        # !!!! все адреса, которые редиректят гостя на страницу логина,
        # !!!! а авторизованному пользователю отдают 200.
        # поведение словаря ниже описывает ответ для гостей.
        cls.private_paths_redirect_guests = {
            "/following/": (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next=/following/"
            ),
            "/create/": (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next=/create/"
            ),
            f"/posts/{cls.own_post.id}/edit/": (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next=/posts/{cls.own_post.id}/edit/"
            ),
        }

        # !!!! все адреса, которые редиректят гостя на страницу логина,
        # !!!! а авторизованного пользователя - на другую страницу.
        # поведение словаря ниже описывает ответ для гостей.
        cls.restricted_paths_redirect_guests = {
            f"/posts/{cls.ones_post.id}/edit/": (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next=/posts/{cls.ones_post.id}/edit/"
            ),
            f"/posts/{cls.own_post.id}/comment/": (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next=/posts/{cls.own_post.id}/comment/"
            ),
            f"/posts/{cls.ones_post.id}/comment/": (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next=/posts/{cls.ones_post.id}/comment/"
            ),
            f"/profile/{cls.user.username}/follow/": (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next=/profile/{cls.user.username}/follow/"
            ),
            f"/profile/{cls.user.username}/unfollow/": (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next=/profile/{cls.user.username}/unfollow/"
            ),
            f"/profile/{cls.other_user.username}/follow/": (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next=/profile/{cls.other_user.username}/follow/"
            ),
            f"/profile/{cls.other_user.username}/unfollow/": (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next=/profile/{cls.other_user.username}/unfollow/"
            ),
            f"/profile/{cls.passion_of_user.username}/follow/": (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next=/profile/{cls.passion_of_user.username}/follow/"
            ),
            f"/profile/{cls.passion_of_user.username}/unfollow/": (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next=/profile/{cls.passion_of_user.username}/unfollow/"
            ),
        }

        # !!!! все адреса, которые редиректят гостя на страницу логина,
        # !!!! а авторизованного пользователя - на другую страницу.
        # поведение словаря ниже описывает ответ для авторизованных клиентов.
        cls.restricted_paths_redirect_auth = {
            f"/posts/{cls.ones_post.id}/edit/": (
                f"/posts/{cls.ones_post.id}/"
            ),
            f"/posts/{cls.own_post.id}/comment/": (
                f"/posts/{cls.own_post.id}/"
            ),
            f"/posts/{cls.ones_post.id}/comment/": (
                f"/posts/{cls.ones_post.id}/"
            ),
            f"/profile/{cls.user.username}/follow/": (
                f"/profile/{cls.user.username}/"
            ),
            f"/profile/{cls.user.username}/unfollow/": (
                f"/profile/{cls.user.username}/"
            ),
            f"/profile/{cls.other_user.username}/follow/": (
                f"/profile/{cls.other_user.username}/"
            ),
            f"/profile/{cls.other_user.username}/unfollow/": (
                f"/profile/{cls.other_user.username}/"
            ),
            f"/profile/{cls.passion_of_user.username}/follow/": (
                f"/profile/{cls.passion_of_user.username}/"
            ),
            f"/profile/{cls.passion_of_user.username}/unfollow/": (
                f"/profile/{cls.passion_of_user.username}/"
            ),
        }

        cls.path_templates_for_guest_users = {
            "/": "posts/index.html",
            f"/group/{cls.group.slug}/": "posts/group_list.html",
            f"/profile/{cls.user.username}/": "posts/profile.html",
            f"/profile/{cls.other_user.username}/": "posts/profile.html",
            f"/posts/{cls.own_post.id}/": "posts/post_detail.html",
            f"/posts/{cls.ones_post.id}/": "posts/post_detail.html",
            "/following/": "users/login.html",
            "/create/": "users/login.html",
            f"/posts/{cls.own_post.id}/edit/": "users/login.html",
            f"/posts/{cls.ones_post.id}/edit/": "users/login.html",
            f"/posts/{cls.own_post.id}/comment/": "users/login.html",
            f"/posts/{cls.ones_post.id}/comment/": "users/login.html",
            f"/profile/{cls.user.username}/follow/": "users/login.html",
            f"/profile/{cls.user.username}/unfollow/": "users/login.html",
            f"/profile/{cls.other_user.username}/follow/": (
                "users/login.html"
            ),
            f"/profile/{cls.other_user.username}/unfollow/": (
                "users/login.html"
            ),
            f"/profile/{cls.passion_of_user.username}/follow/": (
                "users/login.html"
            ),
            f"/profile/{cls.passion_of_user.username}/unfollow/": (
                "users/login.html"
            ),
        }

        cls.path_templates_for_auth_users = {
            "/": "posts/index.html",
            f"/group/{cls.group.slug}/": "posts/group_list.html",
            f"/profile/{cls.user.username}/": "posts/profile.html",
            f"/profile/{cls.other_user.username}/": "posts/profile.html",
            f"/posts/{cls.own_post.id}/": "posts/post_detail.html",
            f"/posts/{cls.ones_post.id}/": "posts/post_detail.html",
            "/following/": "posts/following.html",
            "/create/": "posts/post_create.html",
            f"/posts/{cls.own_post.id}/edit/": "posts/post_create.html",
            f"/posts/{cls.ones_post.id}/edit/": "posts/post_detail.html",
            f"/posts/{cls.own_post.id}/comment/": "posts/post_detail.html",
            f"/posts/{cls.ones_post.id}/comment/": "posts/post_detail.html",
            f"/profile/{cls.user.username}/follow/": "posts/profile.html",
            f"/profile/{cls.user.username}/unfollow/": "posts/profile.html",
            f"/profile/{cls.other_user.username}/follow/": (
                "posts/profile.html"
            ),
            f"/profile/{cls.other_user.username}/unfollow/": (
                "posts/profile.html"
            ),
            f"/profile/{cls.passion_of_user.username}/follow/": (
                "posts/profile.html"
            ),
            f"/profile/{cls.passion_of_user.username}/unfollow/": (
                "posts/profile.html"
            ),
        }

        cls.path_names = {
            "/": reverse_lazy(viewname="posts:index"),
            f"/group/{cls.group.slug}/": reverse_lazy(
                viewname="posts:group_list",
                kwargs={"slug": cls.group.slug},
            ),
            f"/profile/{cls.user.username}/": reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": cls.user.username},
            ),
            f"/profile/{cls.other_user.username}/": reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": cls.other_user.username},
            ),
            f"/posts/{cls.own_post.id}/": reverse_lazy(
                viewname="posts:post_detail",
                kwargs={"post_id": cls.own_post.id},
            ),
            f"/posts/{cls.ones_post.id}/": reverse_lazy(
                viewname="posts:post_detail",
                kwargs={"post_id": cls.ones_post.id},
            ),
            "/following/": reverse_lazy(viewname="posts:follow_index"),
            "/create/": reverse_lazy(viewname="posts:post_create"),
            f"/posts/{cls.own_post.id}/edit/": reverse_lazy(
                viewname="posts:post_edit",
                kwargs={"post_id": cls.own_post.id},
            ),
            f"/posts/{cls.ones_post.id}/edit/": reverse_lazy(
                viewname="posts:post_edit",
                kwargs={"post_id": cls.ones_post.id},
            ),
            f"/posts/{cls.own_post.id}/comment/": reverse_lazy(
                viewname="posts:add_comment",
                kwargs={"post_id": cls.own_post.id},
            ),
            f"/posts/{cls.ones_post.id}/comment/": reverse_lazy(
                viewname="posts:add_comment",
                kwargs={"post_id": cls.ones_post.id},
            ),
            f"/profile/{cls.user.username}/follow/": reverse_lazy(
                viewname="posts:profile_follow",
                kwargs={"username": cls.user.username},
            ),
            f"/profile/{cls.user.username}/unfollow/": reverse_lazy(
                viewname="posts:profile_unfollow",
                kwargs={"username": cls.user.username},
            ),
            f"/profile/{cls.other_user.username}/follow/": reverse_lazy(
                viewname="posts:profile_follow",
                kwargs={"username": cls.other_user.username},
            ),
            f"/profile/{cls.other_user.username}/unfollow/": reverse_lazy(
                viewname="posts:profile_unfollow",
                kwargs={"username": cls.other_user.username},
            ),
            f"/profile/{cls.passion_of_user.username}/follow/": reverse_lazy(
                viewname="posts:profile_follow",
                kwargs={"username": cls.passion_of_user.username},
            ),
            f"/profile/{cls.passion_of_user.username}/unfollow/": reverse_lazy(
                viewname="posts:profile_unfollow",
                kwargs={"username": cls.passion_of_user.username},
            ),
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(user=self.user)

    def test_responses_for_guest_clients(self):
        """
        Проверяется реакция адресов пространства имён posts
        на запросы от гостевых клиентов.
        """

        for path, expected in self.public_paths_status_codes.items():
            with self.subTest(path=path):
                guest_response = self.guest_client.get(
                    path=path, follow=False,
                )
                self.assertEqual(
                    first=guest_response.status_code,
                    second=expected,
                )

        for path, expected in {
            **self.private_paths_redirect_guests,
            **self.restricted_paths_redirect_guests,
        }.items():
            with self.subTest(path=path):
                guest_response = self.guest_client.get(
                    path=path, follow=False,
                )
                self.assertRedirects(
                    response=guest_response,
                    expected_url=expected,
                    status_code=HTTPStatus.FOUND,
                    target_status_code=HTTPStatus.OK,
                )

    def test_responses_for_authorized_clients(self):
        """
        Проверяется реакция адресов пространства имён posts
        на запросы от авторизованных клиентов.
        """

        for path, expected in self.public_paths_status_codes.items():
            with self.subTest(path=path):
                authorized_response = self.authorized_client.get(
                    path=path, follow=False,
                )
                self.assertEqual(
                    first=authorized_response.status_code,
                    second=expected,
                )

        for path in self.private_paths_redirect_guests.keys():
            with self.subTest(path=path):
                authorized_response = self.authorized_client.get(
                    path=path, follow=False,
                )
                self.assertEqual(
                    first=authorized_response.status_code,
                    second=HTTPStatus.OK,
                )

        for path, expected in self.restricted_paths_redirect_auth.items():
            with self.subTest(path=path):
                authorized_response = self.authorized_client.get(
                    path=path, follow=False,
                )
                self.assertRedirects(
                    response=authorized_response,
                    expected_url=expected,
                    status_code=HTTPStatus.FOUND,
                    target_status_code=HTTPStatus.OK,
                )

    def test_posts_urls_use_correct_templates(self):
        """
        Проверяются шаблоны, используемые пространством имён posts,
        при запросах от обоих типов клиентов.
        """

        for path, expected in self.path_templates_for_guest_users.items():
            with self.subTest(path=path):
                guest_response = self.guest_client.get(
                    path=path, follow=True,
                )
                self.assertTemplateUsed(
                    response=guest_response,
                    template_name=expected,
                )

        for path, expected in self.path_templates_for_auth_users.items():
            with self.subTest(path=path):
                authorized_response = self.authorized_client.get(
                    path=path, follow=True,
                )
                self.assertTemplateUsed(
                    response=authorized_response,
                    template_name=expected,
                )

    def test_posts_urls_use_correct_names(self):
        """
        Проверяется корректность имён, используемых адресами
        пространства имён posts.
        """

        for path, expected_name in self.path_names.items():
            with self.subTest(path=path):
                self.assertEqual(
                    first=path,
                    second=expected_name,
                )

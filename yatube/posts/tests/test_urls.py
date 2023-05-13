from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
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

        cls.urls = {
            # public, GET requests only
            "index": "/",
            "group": "/group/",
            "group_slug": f"/group/{cls.group.slug}/",
            "group_non_existent": "/group/non_existent/",
            "profile": "/profile/",
            "profile_self": f"/profile/{cls.user.username}/",
            "profile_other": f"/profile/{cls.other_user.username}/",
            "profile_of_passion": f"/profile/{cls.passion_of_user.username}/",
            "profile_non_existent": "/profile/non_existent/",
            "posts": "/posts/",
            "post_own": f"/posts/{cls.own_post.id}/",
            "post_ones": f"/posts/{cls.ones_post.id}/",
            "post_non_existent": "/posts/69420/",
            # private, GET requests only
            "follow": "/follow/",
            "create": "/create/",
            "edit_own": f"/posts/{cls.own_post.id}/edit/",
            # restricted, GET requests only
            "edit_ones": f"/posts/{cls.ones_post.id}/edit/",
            # restricted, POST requests only
            "comment_on_own": f"/posts/{cls.own_post.id}/comment/",
            "comment_on_ones": f"/posts/{cls.ones_post.id}/comment/",
            "follow_self": f"/profile/{cls.user.username}/follow/",
            "unfollow_self": f"/profile/{cls.user.username}/unfollow/",
            "follow_other": f"/profile/{cls.other_user.username}/follow/",
            "unfollow_other": f"/profile/{cls.other_user.username}/unfollow/",
            "follow_passion": (
                f"/profile/{cls.passion_of_user.username}/follow/"
            ),
            "unfollow_passion": (
                f"/profile/{cls.passion_of_user.username}/unfollow/"
            ),
        }

        cls.public_path_status_codes = {
            cls.urls["index"]: HTTPStatus.OK,
            cls.urls["group"]: HTTPStatus.NOT_FOUND,
            cls.urls["group_slug"]: HTTPStatus.OK,
            cls.urls["group_non_existent"]: HTTPStatus.NOT_FOUND,
            cls.urls["profile"]: HTTPStatus.NOT_FOUND,
            cls.urls["profile_self"]: HTTPStatus.OK,
            cls.urls["profile_other"]: HTTPStatus.OK,
            cls.urls["profile_of_passion"]: HTTPStatus.OK,
            cls.urls["profile_non_existent"]: HTTPStatus.NOT_FOUND,
            cls.urls["posts"]: HTTPStatus.NOT_FOUND,
            cls.urls["post_own"]: HTTPStatus.OK,
            cls.urls["post_ones"]: HTTPStatus.OK,
            cls.urls["post_non_existent"]: HTTPStatus.NOT_FOUND,
        }

        cls.private_path_redirect_guests = {
            cls.urls["follow"]: (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next={cls.urls['follow']}"
            ),
            cls.urls["create"]: (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next={cls.urls['create']}"
            ),
            cls.urls["edit_own"]: (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next={cls.urls['edit_own']}"
            ),
        }

        cls.restricted_getonly_redirect_guests = {
            cls.urls["edit_ones"]: (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next={cls.urls['edit_ones']}"
            ),
        }

        cls.restricted_getonly_redirect_auth = {
            cls.urls["edit_ones"]: (
                f"{cls.urls['post_ones']}"
            ),
        }

        cls.restricted_postonly_redirect_guests = {
            cls.urls["comment_on_own"]: (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next={cls.urls['comment_on_own']}"
            ),
            cls.urls["comment_on_ones"]: (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next={cls.urls['comment_on_ones']}"
            ),
            cls.urls["follow_self"]: (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next={cls.urls['follow_self']}"
            ),
            cls.urls["unfollow_self"]: (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next={cls.urls['unfollow_self']}"
            ),
            cls.urls["follow_other"]: (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next={cls.urls['follow_other']}"
            ),
            cls.urls["unfollow_other"]: (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next={cls.urls['unfollow_other']}"
            ),
            cls.urls["follow_passion"]: (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next={cls.urls['follow_passion']}"
            ),
            cls.urls["unfollow_passion"]: (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next={cls.urls['unfollow_passion']}"
            ),
        }

        cls.restricted_postonly_redirect_auth = {
            cls.urls["comment_on_own"]: (
                f"{cls.urls['post_own']}"
            ),
            cls.urls["comment_on_ones"]: (
                f"{cls.urls['post_ones']}"
            ),
            cls.urls["follow_self"]: (
                f"{cls.urls['profile_self']}"
            ),
            cls.urls["unfollow_self"]: (
                f"{cls.urls['profile_self']}"
            ),
            cls.urls["follow_other"]: (
                f"{cls.urls['profile_other']}"
            ),
            cls.urls["unfollow_other"]: (
                f"{cls.urls['profile_other']}"
            ),
            cls.urls["follow_passion"]: (
                f"{cls.urls['profile_of_passion']}"
            ),
            cls.urls["unfollow_passion"]: (
                f"{cls.urls['profile_of_passion']}"
            ),
        }

        cls.path_names = {
            # public, GET requests only
            cls.urls["index"]: reverse_lazy(viewname="posts:index"),
            cls.urls["group_slug"]: reverse_lazy(
                viewname="posts:group_posts",
                kwargs={"slug": cls.group.slug},
            ),
            cls.urls["profile_self"]: reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": cls.user.username},
            ),
            cls.urls["profile_other"]: reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": cls.other_user.username},
            ),
            cls.urls["profile_of_passion"]: reverse_lazy(
                viewname="posts:profile",
                kwargs={"username": cls.passion_of_user.username},
            ),
            cls.urls["post_own"]: reverse_lazy(
                viewname="posts:post_detail",
                kwargs={"post_id": cls.own_post.id},
            ),
            cls.urls["post_ones"]: reverse_lazy(
                viewname="posts:post_detail",
                kwargs={"post_id": cls.ones_post.id},
            ),
            # private, GET requests only
            cls.urls["follow"]: reverse_lazy(viewname="posts:follow_index"),
            cls.urls["create"]: reverse_lazy(viewname="posts:post_create"),
            cls.urls["edit_own"]: reverse_lazy(
                viewname="posts:post_edit",
                kwargs={"post_id": cls.own_post.id},
            ),
            # restricted, GET requests only
            cls.urls["edit_ones"]: reverse_lazy(
                viewname="posts:post_edit",
                kwargs={"post_id": cls.ones_post.id},
            ),
            # restricted, POST requests only
            cls.urls["comment_on_own"]: reverse_lazy(
                viewname="posts:add_comment",
                kwargs={"post_id": cls.own_post.id},
            ),
            cls.urls["comment_on_ones"]: reverse_lazy(
                viewname="posts:add_comment",
                kwargs={"post_id": cls.ones_post.id},
            ),
            cls.urls["follow_self"]: reverse_lazy(
                viewname="posts:profile_follow",
                kwargs={"username": cls.user.username},
            ),
            cls.urls["unfollow_self"]: reverse_lazy(
                viewname="posts:profile_unfollow",
                kwargs={"username": cls.user.username},
            ),
            cls.urls["follow_other"]: reverse_lazy(
                viewname="posts:profile_follow",
                kwargs={"username": cls.other_user.username},
            ),
            cls.urls["unfollow_other"]: reverse_lazy(
                viewname="posts:profile_unfollow",
                kwargs={"username": cls.other_user.username},
            ),
            cls.urls["follow_passion"]: reverse_lazy(
                viewname="posts:profile_follow",
                kwargs={"username": cls.passion_of_user.username},
            ),
            cls.urls["unfollow_passion"]: reverse_lazy(
                viewname="posts:profile_unfollow",
                kwargs={"username": cls.passion_of_user.username},
            ),
        }

        cls.getonly_templates_for_guest_users = {
            # public, GET requests only
            cls.urls["index"]: "posts/index.html",
            cls.urls["group_slug"]: "posts/group_list.html",
            cls.urls["profile_self"]: "posts/profile.html",
            cls.urls["profile_other"]: "posts/profile.html",
            cls.urls["profile_of_passion"]: "posts/profile.html",
            cls.urls["post_own"]: "posts/post_detail.html",
            cls.urls["post_ones"]: "posts/post_detail.html",
            # private, GET requests only
            cls.urls["follow"]: "users/login.html",
            cls.urls["create"]: "users/login.html",
            cls.urls["edit_own"]: "users/login.html",
            # restricted, GET requests only
            cls.urls["edit_ones"]: "users/login.html",
        }

        cls.postonly_templates_for_guest_users = {
            # restricted, POST requests only
            cls.urls["comment_on_own"]: "users/login.html",
            cls.urls["comment_on_ones"]: "users/login.html",
            cls.urls["follow_self"]: "users/login.html",
            cls.urls["unfollow_self"]: "users/login.html",
            cls.urls["follow_other"]: "users/login.html",
            cls.urls["unfollow_other"]: "users/login.html",
            cls.urls["follow_passion"]: "users/login.html",
            cls.urls["unfollow_passion"]: "users/login.html",
        }

        cls.getonly_templates_for_auth_users = {
            # public, GET requests only
            cls.urls["index"]: "posts/index.html",
            cls.urls["group_slug"]: "posts/group_list.html",
            cls.urls["profile_self"]: "posts/profile.html",
            cls.urls["profile_other"]: "posts/profile.html",
            cls.urls["profile_of_passion"]: "posts/profile.html",
            cls.urls["post_own"]: "posts/post_detail.html",
            cls.urls["post_ones"]: "posts/post_detail.html",
            # private, GET requests only
            cls.urls["follow"]: "posts/follow.html",
            cls.urls["create"]: "posts/post_create.html",
            cls.urls["edit_own"]: "posts/post_create.html",
            # restricted, GET requests only
            cls.urls["edit_ones"]: "posts/post_detail.html",
        }

        cls.postonly_templates_for_auth_users = {
            # restricted, POST requests only
            cls.urls["comment_on_own"]: "posts/post_detail.html",
            cls.urls["comment_on_ones"]: "posts/post_detail.html",
            cls.urls["follow_self"]: "posts/profile.html",
            cls.urls["unfollow_self"]: "posts/profile.html",
            cls.urls["follow_other"]: "posts/profile.html",
            cls.urls["unfollow_other"]: "posts/profile.html",
            cls.urls["follow_passion"]: "posts/profile.html",
            cls.urls["unfollow_passion"]: "posts/profile.html",
        }

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(user=self.user)

    def tearDown(self):
        cache.clear()

    def test_responses_for_guest_clients(self):
        """
        Проверяется реакция адресов пространства имён posts
        на запросы от гостевых клиентов.
        """

        for path, expected in self.public_path_status_codes.items():
            with self.subTest(path=path):
                guest_response = self.guest_client.get(
                    path=path, follow=False,
                )
                self.assertEqual(
                    first=guest_response.status_code,
                    second=expected,
                )

        for path, expected in {
            **self.private_path_redirect_guests,
            **self.restricted_getonly_redirect_guests,
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

        for path, expected in self.restricted_postonly_redirect_guests.items():
            with self.subTest(path=path):
                guest_response = self.guest_client.post(
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

        for path, expected in self.public_path_status_codes.items():
            with self.subTest(path=path):
                authorized_response = self.authorized_client.get(
                    path=path, follow=False,
                )
                self.assertEqual(
                    first=authorized_response.status_code,
                    second=expected,
                )

        for path in self.private_path_redirect_guests.keys():
            with self.subTest(path=path):
                authorized_response = self.authorized_client.get(
                    path=path, follow=False,
                )
                self.assertEqual(
                    first=authorized_response.status_code,
                    second=HTTPStatus.OK,
                )

        for path, expected in self.restricted_getonly_redirect_auth.items():
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

        for path, expected in self.restricted_postonly_redirect_auth.items():
            with self.subTest(path=path):
                authorized_response = self.authorized_client.post(
                    path=path, follow=False,
                )
                self.assertRedirects(
                    response=authorized_response,
                    expected_url=expected,
                    status_code=HTTPStatus.FOUND,
                    target_status_code=HTTPStatus.OK,
                )

    def test_posts_urls_use_correct_names(self):
        """Проверка имён адресов пространства имён posts"""

        for path, expected in self.path_names.items():
            with self.subTest(path=path):
                self.assertEqual(
                    first=path,
                    second=expected,
                )

    def test_posts_urls_use_correct_templates_for_guests(self):
        """
        Проверка шаблонов адресов пространства имён posts
        для гостевых клиентов
        """

        for path, expected in self.getonly_templates_for_guest_users.items():
            with self.subTest(path=path):
                guest_response = self.guest_client.get(
                    path=path, follow=True,
                )
                self.assertTemplateUsed(
                    response=guest_response,
                    template_name=expected,
                )

        for path, expected in self.postonly_templates_for_guest_users.items():
            with self.subTest(path=path):
                guest_response = self.guest_client.post(
                    path=path, follow=True,
                )
                self.assertTemplateUsed(
                    response=guest_response,
                    template_name=expected,
                )

    def test_posts_urls_use_correct_templates_for_auth(self):
        """
        Проверка шаблонов адресов пространства имён posts
        для авторизованных клиентов
        """

        for path, expected in self.getonly_templates_for_auth_users.items():
            with self.subTest(path=path):
                authorized_response = self.authorized_client.get(
                    path=path, follow=True,
                )
                self.assertTemplateUsed(
                    response=authorized_response,
                    template_name=expected,
                )

        for path, expected in self.postonly_templates_for_auth_users.items():
            with self.subTest(path=path):
                authorized_response = self.authorized_client.post(
                    path=path, follow=True,
                )
                self.assertTemplateUsed(
                    response=authorized_response,
                    template_name=expected,
                )

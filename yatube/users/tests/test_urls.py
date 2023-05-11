from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse_lazy

User = get_user_model()


class UsersURLsTests(TestCase):
    """Набор тестов для проверки адресов пространства имён users"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username="test_username",
        )

        cls.public_paths_status_codes = {
            "/auth/": HTTPStatus.NOT_FOUND,
            "/auth/login/": HTTPStatus.OK,
            "/auth/logout/": HTTPStatus.OK,
            "/auth/signup/": HTTPStatus.OK,
            "/auth/password_reset/": HTTPStatus.OK,
            "/auth/password_reset/done/": HTTPStatus.OK,
            "/auth/password_reset/confirm/": HTTPStatus.NOT_FOUND,
            "/auth/password_reset/complete/": HTTPStatus.OK,
            "/auth/non_existing_path/": HTTPStatus.NOT_FOUND,
        }

        cls.private_paths_redirect_urls = {
            "/auth/password_change/": (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next=/auth/password_change/"
            ),
            "/auth/password_change/done/": (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next=/auth/password_change/done/"
            ),
        }

        cls.public_paths_templates = {
            "/auth/login/": "users/login.html",
            "/auth/signup/": "users/signup.html",
            "/auth/password_reset/": "users/password_reset.html",
            "/auth/password_reset/done/": "users/password_reset_done.html",
            "/auth/password_reset/complete/":
                "users/password_reset_complete.html",
            "/auth/logout/": "users/logout.html",
        }

        cls.private_paths_templates = {
            "/auth/password_change/": "users/password_change.html",
            "/auth/password_change/done/": "users/password_change_done.html",
        }

        cls.public_names_templates = {
            reverse_lazy(
                viewname="users:login",
            ): "users/login.html",
            reverse_lazy(
                viewname="users:signup",
            ): "users/signup.html",
            reverse_lazy(
                viewname="users:password_reset",
            ): "users/password_reset.html",
            reverse_lazy(
                viewname="users:password_reset_done",
            ): "users/password_reset_done.html",
            reverse_lazy(
                viewname="users:password_reset_complete",
            ): "users/password_reset_complete.html",
            reverse_lazy(
                viewname="users:logout",
            ): "users/logout.html",
        }

        cls.private_names_templates = {
            reverse_lazy(
                viewname="users:password_change",
            ): "users/password_change.html",
            reverse_lazy(
                viewname="users:password_change_done",
            ): "users/password_change_done.html",
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(user=self.user)

    def test_users_public_urls_exist_at_desired_locations(self):
        """
        Проверка общедоступных адресов пространства имён users.
        Проверяется реакция при запросе от обоих типов клиентов.
        """

        for path, expected in self.public_paths_status_codes.items():
            with self.subTest(path=path):
                guest_response = self.guest_client.get(
                    path=path, follow=False,
                )
                authorized_response = self.authorized_client.get(
                    path=path, follow=False,
                )
                self.assertEqual(
                    first=guest_response.status_code,
                    second=expected,
                )
                self.assertEqual(
                    first=authorized_response.status_code,
                    second=expected,
                )

    def test_users_private_urls_response_for_guest_users(self):
        """
        Проверка адресов пространства имён users,
        доступных только авторизованным пользователям.
        Проверяется реакция при запросе от гостевого клиента.
        """

        for path, expected in self.private_paths_redirect_urls.items():
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

    def test_users_private_urls_response_for_authorized_users(self):
        """
        Проверка адресов пространства имён users,
        Доступных только авторизованным пользователям.
        Проверяется реакция при запросе от авторизованного клиента.
        """

        for path in self.private_paths_redirect_urls.keys():
            with self.subTest(path=path):
                authorized_response = self.authorized_client.get(
                    path=path, follow=False,
                )
                self.assertEqual(
                    first=authorized_response.status_code,
                    second=HTTPStatus.OK,
                )

    def test_users_urls_use_correct_templates_for_guest_users(self):
        """
        Проверка шаблонов для URL адресов пространства имён users.
        Проверяется реакция при запросе от гостевого клиента.
        """

        for path in self.private_paths_templates.keys():
            with self.subTest(path=path):
                guest_response = self.guest_client.get(
                    path=path, follow=True,
                )
                self.assertTemplateUsed(
                    response=guest_response,
                    template_name="users/login.html",
                )

        for path, expected in self.public_paths_templates.items():
            with self.subTest(path=path):
                guest_response = self.guest_client.get(
                    path=path, follow=True,
                )
                self.assertTemplateUsed(
                    response=guest_response,
                    template_name=expected,
                )

    def test_users_urls_use_correct_templates_for_authorized_users(self):
        """
        Проверка шаблонов для URL адресов пространства имён users.
        Проверяется реакция при запросе от авторизованного клиента.
        """

        for path, expected in self.private_paths_templates.items():
            with self.subTest(path=path):
                authorized_response = self.authorized_client.get(
                    path=path, follow=True,
                )
                self.assertTemplateUsed(
                    response=authorized_response,
                    template_name=expected,
                )

        for path, expected in self.public_paths_templates.items():
            with self.subTest(path=path):
                authorized_response = self.authorized_client.get(
                    path=path, follow=True,
                )
                self.assertTemplateUsed(
                    response=authorized_response,
                    template_name=expected,
                )

    def test_users_names_use_correct_templates_for_guest_users(self):
        """
        Проверка шаблонов для имён адресов пространства имён users.
        Проверяется реакция при запросе от гостевого клиента.
        """

        for name in self.private_names_templates.keys():
            with self.subTest(name=name):
                guest_response = self.guest_client.get(
                    path=name, follow=True,
                )
                self.assertTemplateUsed(
                    response=guest_response,
                    template_name="users/login.html",
                )

        for name, expected in self.public_names_templates.items():
            with self.subTest(name=name):
                guest_response = self.guest_client.get(
                    path=name, follow=True,
                )
                self.assertTemplateUsed(
                    response=guest_response,
                    template_name=expected,
                )

    def test_users_names_use_correct_templates_for_authorized_users(self):
        """
        Проверка шаблонов для имён адресов пространства имён users.
        Проверяется реакция при запросе от авторизованного клиента.
        """

        for name, expected in self.private_names_templates.items():
            with self.subTest(name=name):
                authorized_response = self.authorized_client.get(
                    path=name, follow=True,
                )
                self.assertTemplateUsed(
                    response=authorized_response,
                    template_name=expected,
                )

        for name, expected in self.public_names_templates.items():
            with self.subTest(name=name):
                authorized_response = self.authorized_client.get(
                    path=name, follow=True,
                )
                self.assertTemplateUsed(
                    response=authorized_response,
                    template_name=expected,
                )

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

        cls.urls = {
            # public
            "auth": "/auth/",
            "login": "/auth/login/",
            "signup": "/auth/signup/",
            "reset": "/auth/reset/",
            "reset_done": "/auth/reset/done/",
            "reset_confirm": "/auth/reset/confirm/",
            "reset_complete": "/auth/reset/complete/",
            "non_existent": "/auth/non_existent/",
            # private
            "change": "/auth/change/",
            "change_done": "/auth/change/done/",
            # public, always last in the queue for testing purposes
            "logout": "/auth/logout/",
        }

        # TODO fix /auth/reset/confirm/ path
        cls.public_path_status_codes = {
            cls.urls["auth"]: HTTPStatus.NOT_FOUND,
            cls.urls["login"]: HTTPStatus.OK,
            cls.urls["signup"]: HTTPStatus.OK,
            cls.urls["reset"]: HTTPStatus.OK,
            cls.urls["reset_done"]: HTTPStatus.OK,
            cls.urls["reset_confirm"]: HTTPStatus.NOT_FOUND,
            cls.urls["reset_complete"]: HTTPStatus.OK,
            cls.urls["non_existent"]: HTTPStatus.NOT_FOUND,
            cls.urls["logout"]: HTTPStatus.OK,
        }

        cls.private_path_redirect_guests = {
            cls.urls["change"]: (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next={cls.urls['change']}"
            ),
            cls.urls["change_done"]: (
                f"{reverse_lazy(viewname='users:login')}"
                f"?next={cls.urls['change_done']}"
            ),
        }

        # TODO add /auth/reset/confirm/ path
        cls.path_names = {
            # public
            cls.urls["login"]: reverse_lazy(viewname="users:login"),
            cls.urls["signup"]: reverse_lazy(viewname="users:signup"),
            cls.urls["reset"]: reverse_lazy(viewname="users:reset"),
            cls.urls["reset_done"]: reverse_lazy(viewname="users:reset_done"),
            cls.urls["reset_complete"]: reverse_lazy("users:reset_complete"),
            # private
            cls.urls["change"]: reverse_lazy(viewname="users:change"),
            cls.urls["change_done"]: reverse_lazy("users:change_done"),
            # public, always last in the queue for testing purposes
            cls.urls["logout"]: reverse_lazy(viewname="users:logout"),
        }

        # TODO add /auth/reset/confirm/ path
        cls.path_templates_for_guest_users = {
            # public
            cls.urls["login"]: "users/login.html",
            cls.urls["signup"]: "users/signup.html",
            cls.urls["reset"]: "users/reset.html",
            cls.urls["reset_done"]: "users/reset_done.html",
            cls.urls["reset_complete"]: "users/reset_complete.html",
            # private
            cls.urls["change"]: "users/login.html",
            cls.urls["change_done"]: "users/login.html",
            # public, always last in the queue for testing purposes
            cls.urls["logout"]: "users/logout.html",
        }

        # TODO add /auth/reset/confirm/ path
        cls.path_templates_for_auth_users = {
            # public
            cls.urls["login"]: "users/login.html",
            cls.urls["signup"]: "users/signup.html",
            cls.urls["reset"]: "users/reset.html",
            cls.urls["reset_done"]: "users/reset_done.html",
            cls.urls["reset_complete"]: "users/reset_complete.html",
            # private
            cls.urls["change"]: "users/change.html",
            cls.urls["change_done"]: "users/change_done.html",
            # public, always last in the queue for testing purposes
            cls.urls["logout"]: "users/logout.html",
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(user=self.user)

    def test_responses_for_guest_clients(self):
        """
        Проверяется реакция адресов пространства имён users
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

        for path, expected in self.private_path_redirect_guests.items():
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
        Проверяется реакция адресов пространства имён users
        на запросы от авторизованных клиентов.
        """

        for path in self.private_path_redirect_guests.keys():
            with self.subTest(path=path):
                authorized_response = self.authorized_client.get(
                    path=path, follow=False,
                )
                self.assertEqual(
                    first=authorized_response.status_code,
                    second=HTTPStatus.OK,
                )

        for path, expected in self.public_path_status_codes.items():
            with self.subTest(path=path):
                authorized_response = self.authorized_client.get(
                    path=path, follow=False,
                )
                self.assertEqual(
                    first=authorized_response.status_code,
                    second=expected,
                )

    def test_users_urls_use_correct_names(self):
        """Проверка имён адресов пространства имён users"""

        for path, expected in self.path_names.items():
            with self.subTest(path=path):
                self.assertEqual(
                    first=path,
                    second=expected,
                )

    def test_users_urls_use_correct_templates(self):
        """Проверка шаблонов адресов пространства имён users"""

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

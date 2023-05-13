from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse_lazy

User = get_user_model()


class AboutURLsTests(TestCase):
    """Набор тестов для проверки адресов пространства имён about"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username="test_username",
        )

        cls.urls = {
            # public
            "about": "/about/",
            "tech": "/about/tech/",
            "author": "/about/author/",
            "non_existent": "/about/non_existent/",
        }

        cls.path_status_codes = {
            cls.urls["about"]: HTTPStatus.NOT_FOUND,
            cls.urls["tech"]: HTTPStatus.OK,
            cls.urls["author"]: HTTPStatus.OK,
            cls.urls["non_existent"]: HTTPStatus.NOT_FOUND,
        }

        cls.path_names = {
            cls.urls["tech"]: reverse_lazy(viewname="about:tech"),
            cls.urls["author"]: reverse_lazy(viewname="about:author"),
        }

        cls.path_templates = {
            cls.urls["tech"]: "about/tech.html",
            cls.urls["author"]: "about/author.html",
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(user=self.user)        

    def test_about_urls_exist_at_desired_locations(self):
        """Проверка доступности адресов пространства имён about"""

        for path, expected in self.path_status_codes.items():
            with self.subTest(path=path):
                guest_response = self.guest_client.get(
                    path=path, follow=False,
                )
                self.assertEqual(
                    first=guest_response.status_code,
                    second=expected,
                )

        for path, expected in self.path_status_codes.items():
            with self.subTest(path=path):
                authorized_response = self.authorized_client.get(
                    path=path, follow=False,
                )
                self.assertEqual(
                    first=authorized_response.status_code,
                    second=expected,
                )

    def test_about_urls_use_correct_names(self):
        """Проверка имён адресов пространства имён about"""

        for path, expected in self.path_names.items():
            with self.subTest(path=path):
                self.assertEqual(
                    first=path,
                    second=expected,
                )

    def test_about_urls_use_correct_templates(self):
        """Проверка шаблонов адресов пространства имён about"""

        for path, expected in self.path_templates.items():
            with self.subTest(path=path):
                guest_response = self.guest_client.get(
                    path=path, follow=True,
                )
                self.assertTemplateUsed(
                    response=guest_response,
                    template_name=expected,
                )

        for path, expected in self.path_templates.items():
            with self.subTest(path=path):
                authorized_response = self.authorized_client.get(
                    path=path, follow=True,
                )
                self.assertTemplateUsed(
                    response=authorized_response,
                    template_name=expected,
                )

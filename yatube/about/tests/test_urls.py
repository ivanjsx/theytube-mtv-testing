from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse_lazy


class AboutURLsTests(TestCase):
    """Набор тестов для проверки адресов пространства имён about"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.paths_status_codes = {
            "/about/": HTTPStatus.NOT_FOUND,
            "/about/tech/": HTTPStatus.OK,
            "/about/author/": HTTPStatus.OK,
            "/about/non_existing_path/": HTTPStatus.NOT_FOUND,
        }

        cls.paths_templates = {
            "/about/author/": "about/author.html",
            "/about/tech/": "about/tech.html",
        }

        cls.names_templates = {
            reverse_lazy(viewname="about:author"): "about/author.html",
            reverse_lazy(viewname="about:tech"): "about/tech.html",
        }

    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exist_at_desired_locations(self):
        """Проверка доступности адресов пространства имён about"""

        for path, expected in self.paths_status_codes.items():
            with self.subTest(path=path):
                guest_response = self.guest_client.get(path=path, follow=False)
                self.assertEqual(
                    first=guest_response.status_code,
                    second=expected,
                )

    def test_about_urls_use_correct_templates(self):
        """Проверка шаблонов для URL адресов пространства имён about"""

        for path, expected in self.paths_templates.items():
            with self.subTest(path=path):
                guest_response = self.guest_client.get(path=path, follow=True)
                self.assertTemplateUsed(
                    response=guest_response,
                    template_name=expected,
                )

    def test_about_names_use_correct_templates(self):
        """Проверка шаблонов для имён адресов пространства имён about"""

        for path, expected in self.names_templates.items():
            with self.subTest(path=path):
                guest_response = self.guest_client.get(path=path, follow=True)
                self.assertTemplateUsed(
                    response=guest_response,
                    template_name=expected,
                )

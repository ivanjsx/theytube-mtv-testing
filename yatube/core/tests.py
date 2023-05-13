from http import HTTPStatus

from django.test import Client, TestCase


class CoreTests(TestCase):
    """Набор тестов для проверки работы приложения core"""

    def setUp(self):
        self.guest_client = Client()

    def test_404_error_page(self):
        guest_response = self.guest_client.get(
            path="/non_existent/",
            follow=False,
        )
        self.assertEqual(
            first=guest_response.status_code,
            second=HTTPStatus.NOT_FOUND,
        )
        self.assertTemplateUsed(
            response=guest_response,
            template_name="core/404.html",
        )

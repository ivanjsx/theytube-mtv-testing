from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UsernameField
from django.test import Client, TestCase
from django.urls import reverse_lazy

User = get_user_model()


class UsersViewsTests(TestCase):
    """Набор тестов для проверки вью-функций пространства имён users"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username="test_username",
        )

        cls.form_fields = {
            # (field_name, expected_type, expected_initial_value, ),
            ("username", UsernameField, None, ),
            ("password1", forms.fields.CharField, None, ),
            ("password2", forms.fields.CharField, None, ),
            ("first_name", forms.fields.CharField, None, ),
            ("last_name", forms.fields.CharField, None, ),
            ("email", forms.fields.EmailField, None, ),
        }

        cls.test_form_data_other_username = {
            "username": "completely_different_test_username",
            "password1": "incredibly_strong_password",
            "password2": "incredibly_strong_password",
        }

        cls.test_form_data_same_username = {
            "username": "test_username",
            "password1": "incredibly_strong_password",
            "password2": "incredibly_strong_password",
        }

    def setUp(self):
        self.guest_client = Client()

    def test_signup_form_shows_correct_field_types(self):
        """
        У формы в signup правильное количество полей.
        Их типы и начальные значения совпадают с ожидаемыми.
        """

        guest_client = self.guest_client.get(
            path=reverse_lazy(viewname="users:signup"), follow=False,
        )

        form_fields_count = len(guest_client.context["form"].fields)
        self.assertEqual(
            first=len(self.form_fields),
            second=form_fields_count,
        )

        for name, expected_type, expected_initial_value in self.form_fields:
            with self.subTest(name=name):
                form_field = guest_client.context["form"].fields[name]
                initial_value = form_field.initial
                self.assertIsInstance(
                    obj=form_field,
                    cls=expected_type,
                )
                self.assertEqual(
                    first=initial_value,
                    second=expected_initial_value,
                )

    def test_created_user_shows_up_in_database(self):
        """Созданный пользователь появляется в базе данных."""

        initial_users_count = User.objects.count()

        self.guest_client.post(
            path=reverse_lazy(viewname="users:signup"),
            data=self.test_form_data_other_username,
            follow=True,
        )

        self.assertTrue(
            User.objects.filter(
                username=self.test_form_data_other_username["username"],
            ).exists()
        )

        created_user = User.objects.latest("date_joined")

        self.assertEqual(
            first=User.objects.count(),
            second=initial_users_count + 1,
        )
        self.assertEqual(
            first=created_user.username,
            second=self.test_form_data_other_username["username"],
        )

    def test_cannot_create_user_with_existing_username(self):
        """
        Нельзя создать пользователя с уже существующим логином,
        Но ничего при этом не ломается.
        """

        initial_users_count = User.objects.count()

        guest_response = self.guest_client.post(
            path=reverse_lazy(viewname="users:signup"),
            data=self.test_form_data_same_username,
            follow=True,
        )

        self.assertEqual(
            first=User.objects.count(),
            second=initial_users_count,
        )
        self.assertFormError(
            response=guest_response,
            form="form",
            field="username",
            errors="A user with that username already exists.",
        )
        self.assertEqual(
            first=guest_response.status_code,
            second=HTTPStatus.OK,
        )

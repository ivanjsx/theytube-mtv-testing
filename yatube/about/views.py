from django.views.generic.base import TemplateView


class AuthorView(TemplateView):
    """Показать страницу Об авторе"""

    template_name = "about/author.html"


class TechView(TemplateView):
    """Показать страницу О технологиях"""

    template_name = "about/tech.html"

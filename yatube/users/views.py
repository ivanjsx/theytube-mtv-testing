from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import CreationForm


class SignUpView(CreateView):
    """Показывает страницу регистрации нового пользователя"""

    form_class = CreationForm
    success_url = reverse_lazy(viewname="posts:index")
    template_name = "users/signup.html"

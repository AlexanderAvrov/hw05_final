from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.core.cache import cache

from .forms import CreationForm


class SignUp(CreateView):
    """Вью-класс для создания пользователя"""

    cache.clear()
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'

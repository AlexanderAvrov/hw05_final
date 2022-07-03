from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Вью-класс для отображения страницы про автора."""

    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Вью-класс для отображения страницы про технологии."""

    template_name = 'about/tech.html'

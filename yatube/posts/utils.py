from django.core.paginator import Paginator

from .constants import POSTS_LIMIT


def get_ten_posts_per_page(request, post_list):
    """Функция-утилита для Пагинации страниц"""
    paginator = Paginator(post_list, POSTS_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj

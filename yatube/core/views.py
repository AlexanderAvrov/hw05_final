from django.shortcuts import render


def page_not_found(request, exception):
    """View функция страницы 404"""

    return render(
        request,
        'core/404.html',
        {'path': request.path},
        status=404,
    )


def csrf_failure(request, reason=''):
    """View функция страницы 403 (ошибка проверки csrf)"""

    return render(request, 'core/403csrf.html')


def server_error(request):
    """View функция страницы 500"""

    return render(request, 'core/500.html', status=500)


def permission_denied(request, exception):
    """View функция страницы 403"""

    return render(request, 'core/403.html', status=403)

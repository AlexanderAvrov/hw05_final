from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersUrlTests(TestCase):
    """Тесты для проверки urls приложения Posts"""

    def setUp(self):
        # неавторизованный клиент
        self.guest_client = Client()
        # авторизованный клиент
        self.user = User.objects.create_user(username='noname')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон в users."""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html',
            '/auth/password-reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_userapp_existing(self):
        """Тесты страниц на код 200"""
        urls = (
            '/auth/signup/',
            '/auth/logout/',
            '/auth/login/',
            '/auth/password-reset/',
            '/auth/password_reset/done/',
            '/auth/reset/done/',
        )
        for url in urls:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

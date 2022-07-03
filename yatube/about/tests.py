from django.test import Client, TestCase


class AboutsUrlTests(TestCase):
    """Тесты для проверки urls.py"""

    def setUp(self):
        self.guest_client = Client()

    def test_urls_about_exists(self):
        """Тесты доступности страниц приложения about"""
        urls = (
            '/about/author/',
            '/about/tech/',
        )
        for url in urls:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_templates_about_(self):
        """Тесты проверки шаблонов страниц приложения about"""
        templates_urls = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for address, template in templates_urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

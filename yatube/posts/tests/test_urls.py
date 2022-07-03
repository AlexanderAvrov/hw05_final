from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from ..models import Group, Post

User = get_user_model()


class PostsUrlTests(TestCase):
    """Тесты для проверки urls приложения Posts"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Test_group',
            slug='test-slug',
            description='Test_description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.INDEX = reverse('posts:index')
        cls.GROUP_LIST = reverse(
            'posts:group_list',
            kwargs={'slug': cls.group.slug},
        )
        cls.PROFILE = reverse('posts:profile', kwargs={'username': cls.user})
        cls.DETAIL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.id},
        )
        cls.CREATE = reverse('posts:post_create')
        cls.EDIT = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post.id},
        )
        cls.LOGIN = reverse('users:login')

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='noname')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user_author = User.objects.get(username='author')
        self.post_author = Client()
        self.post_author.force_login(self.user_author)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        reverses_and_templates = {
            self.INDEX: 'posts/index.html',
            self.GROUP_LIST: 'posts/group_list.html',
            self.PROFILE: 'posts/profile.html',
            self.DETAIL: 'posts/post_detail.html',
            self.CREATE: 'posts/create_post.html',
            self.EDIT: 'posts/create_post.html',
        }
        for address, template in reverses_and_templates.items():
            with self.subTest(address=address):
                response = self.post_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_exists_at_desired_location_authorized(self):
        """Тесты доступности страниц для неавторизованного пользователя"""
        reverses = (
            self.INDEX,
            self.GROUP_LIST,
            self.PROFILE,
            self.DETAIL,
        )
        for url in reverses:
            with self.subTest(value=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_page_exists(self):
        """Тест доступа к /create/ для авторизованного пользователя"""
        response = self.authorized_client.get(self.CREATE)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_page_exists(self):
        """Тест доступа к post_edit для авторизованного пользователя"""
        response = self.post_author.get(self.EDIT)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        """Тест несуществующей страницы и шаблона к статусу 404"""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_confidentiality_pages_for_guest_clien(self):
        """Доступ к post_edit и post_create для неавторизованного юзера"""
        responses = (
            self.client.get(self.CREATE),
            self.client.get(self.EDIT),
        )
        for response in responses:
            with self.subTest():
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_edit_page_for_not_author(self):
        """Тест доступа к post_edit для не автора публикации"""
        response = self.authorized_client.get(self.EDIT)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_redirects_for_guest_client(self):
        """Проверка редиректа на страницах закрытых для гостей"""
        response = self.client.get(self.CREATE)
        self.assertRedirects(response, f'{self.LOGIN}?next={self.CREATE}')
        response = self.client.get(self.EDIT)
        self.assertRedirects(response, f'{self.LOGIN}?next={self.EDIT}')

    def test_redirect_for_not_author_edit_post(self):
        """Проверка редиректа при редактировании чужого поста"""
        response = self.authorized_client.get(self.EDIT)
        self.assertRedirects(response, self.DETAIL)

import shutil
import tempfile

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.conf import settings

from ..constants import POSTS_LIMIT
from ..models import Group, Post, Follow, Comment

User = get_user_model()
SECOND_PAGE_COUNT_POST = 3
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    """Проверка вью функций приложения Posts"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Test_group',
            slug='test-slug',
            description='Test_description',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif',
        )
        cls.posts = [
            Post(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group,
                image=cls.uploaded,
            )
            for i in range(POSTS_LIMIT + SECOND_PAGE_COUNT_POST)
        ]
        Post.objects.bulk_create(cls.posts)
        cls.posts = Post.objects.all()
        cls.INDEX = reverse('posts:index')
        cls.GROUP_LIST = reverse(
            'posts:group_list',
            kwargs={'slug': cls.group.slug},
        )
        cls.PROFILE = reverse('posts:profile', kwargs={'username': cls.user})
        cls.DETAIL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.posts[0].id},
        )
        cls.CREATE = reverse('posts:post_create')
        cls.EDIT = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.posts[0].id},
        )
        cls.LOGIN = reverse('users:login')
        cls.FOLLOW = reverse('posts:follow_index')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.user_0 = User.objects.create_user(username='noname')
        self.logined_client = Client()
        self.logined_client.force_login(self.user_0)
        self.user = User.objects.get(username='author')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """Вью использует правильные шаблоны."""
        templates_pages_names = {
            self.INDEX: 'posts/index.html',
            self.GROUP_LIST: 'posts/group_list.html',
            self.PROFILE: 'posts/profile.html',
            self.DETAIL: 'posts/post_detail.html',
            self.CREATE: 'posts/create_post.html',
            self.EDIT: 'posts/create_post.html',
            self.FOLLOW: 'posts/follow.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_of_post_app_about_context(self):
        """Проверка контекста постов на главной, странице групп и профиля"""
        pages = (
            self.INDEX,
            self.GROUP_LIST,
            self.PROFILE,
        )
        for page in pages:
            with self.subTest(value=page):
                response = self.authorized_client.get(page)
                context_post = response.context['page_obj'][0]
                self.assertEqual(context_post.text, self.posts[0].text)
                self.assertEqual(context_post.id, self.posts[0].id)
                self.assertEqual(
                    context_post.author.username,
                    self.user.username,
                )
                self.assertEqual(context_post.group.title, self.group.title)
                self.assertEqual(context_post.image, self.posts[0].image)

    def test_paginator_posts_pages_contains_ten_records(self):
        """На страницы приложения posts выводится по 10 постов"""
        pages = (
            self.INDEX,
            self.GROUP_LIST,
            self.PROFILE,
        )
        for reverses in pages:
            with self.subTest(value=reverses):
                response = self.authorized_client.get(reverses)
                self.assertEqual(
                    len(response.context['page_obj']),
                    POSTS_LIMIT
                )

    def test_second_posts_pages_contains_three_records(self):
        """Проверка: на второй странице паджинации должно быть три поста."""
        pages = (
            self.INDEX + '?page=2',
            self.GROUP_LIST + '?page=2',
            self.PROFILE + '?page=2',
        )
        for reverses in pages:
            with self.subTest(value=reverses):
                response = self.authorized_client.get(reverses)
                self.assertEqual(
                    len(response.context['page_obj']),
                    SECOND_PAGE_COUNT_POST,
                )

    def test_group_page_show_correct_context(self):
        """Шаблон group_list.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.GROUP_LIST)
        group_from_context = response.context['group']
        self.assertEqual(group_from_context, self.group)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile.html сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.PROFILE)
        self.assertEqual(response.context['author'], self.user)
        self.assertIn(response.context['following'], [True, False])

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail.html сформирован с правильным контекстом."""
        Comment.objects.create(
            text='test_Comment',
            author=self.user,
            post=self.posts[0],
        )
        response = self.authorized_client.get(self.DETAIL)
        form_fields = {'text': forms.fields.CharField}
        form_field = response.context.get('form').fields.get('text')
        self.assertIsInstance(form_field, form_fields['text'])
        self.assertEqual(response.context['post'].text, self.posts[1].text)
        self.assertEqual(response.context['post'].id, self.posts[0].id)
        self.assertEqual(response.context['post'].author, self.user)
        self.assertEqual(response.context['post'].group, self.group)
        self.assertEqual(response.context['post'].image, self.posts[0].image)
        self.assertEqual(
            response.context['comments'][0],
            self.posts[0].comments.select_related('post', 'author')[0],
        )
        self.assertIn(response.context['following'], [True, False])

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.CREATE)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.EDIT)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['post'].text, self.posts[1].text)
        self.assertTrue(response.context['is_edit'])

    def test_group_shows_new_post_on_pages(self):
        """Пост попадает на главную страницу, в свою группу и профиль автора"""
        user = User.objects.create_user(username='new_author')
        group = Group.objects.create(title='new_group', slug='new-slug')
        post = Post.objects.create(
            author=user,
            text='новый пост',
            group=group,
        )
        pages = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': group.slug}),
            reverse('posts:profile', kwargs={'username': user.username}),
        )
        for reverses in pages:
            with self.subTest(value=reverses):
                response = self.authorized_client.get(reverses)
                self.assertEqual(
                    response.context.get('page_obj').object_list[0],
                    post,
                )

    def test_post_dont_shows_at_another_pages(self):
        """Пост не попадает в чужую группу и профиль автора"""
        user = User.objects.create_user(username='new_author')
        group = Group.objects.create(title='new_group', slug='new-slug')
        post = Post.objects.create(
            author=user,
            text='новый пост',
            group=group,
        )
        pages = (
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        )
        for reverses in pages:
            with self.subTest(value=reverses):
                response = self.authorized_client.get(reverses)
                self.assertNotIn(
                    post,
                    response.context.get('page_obj').object_list,
                )

    def test_cache_index_page(self):
        """Кеширование главной страницы работает"""
        post = Post.objects.create(
            author=self.user,
            text='post for test cache',
        )
        content_index = self.client.get(self.INDEX).content
        post.delete()
        content_index_after_delete = self.client.get(self.INDEX).content
        self.assertEqual(content_index, content_index_after_delete)
        cache.clear()
        content_index_after_cache_clear = self.client.get(self.INDEX).content
        self.assertNotEqual(
            content_index_after_cache_clear,
            content_index_after_delete,
        )

    def test_following_for_users(self):
        """Авторизованый пользователь создаёт подписку"""
        follow_count = Follow.objects.count()
        self.logined_client.get(reverse(
            'posts:profile_follow',
            args=[self.user.username],
        ))
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        follow = Follow.objects.latest(id)
        self.assertEqual(follow.user, self.logined_client)
        self.assertEqual(follow.author, self.user)

    def test_following_for_users(self):
        """Неавторизованый пользователь не может создать подписку"""
        follow_count = Follow.objects.count()
        self.client.get(reverse(
            'posts:profile_follow',
            args=[self.user.username],
        ))
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_following_for_users(self):
        """Пользователь не может подписаться на сомого себя"""
        follow_count = Follow.objects.count()
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            args=[self.user.username],
        ))
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_following_for_users(self):
        """Авторизованый пользователь удаляет подписки"""
        Follow.objects.create(user=self.user_0, author=self.user)
        follow_count = Follow.objects.count()
        self.logined_client.get(reverse(
            'posts:profile_unfollow',
            args=[self.user.username],
        ))
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_new_post_shows_on_follow_page(self):
        """Только подписчик видит новую запись пол-ля на странице подписок"""
        self.logined_client.get(reverse(
            'posts:profile_follow',
            args=[self.user.username],
        ))
        Post.objects.create(
            text='Текст для проверки подписок',
            author=self.user,
        )
        response_follow_index = self.logined_client.get(reverse(
            'posts:follow_index',
        ))
        self.assertEqual(
            response_follow_index.context['page_obj'].object_list[0],
            Post.objects.first(),
        )

    def test_new_post_dont_shows_on_unfollow_page(self):
        """Неподписчик не видит новую запись пол-ля на странице подписок"""
        Post.objects.create(
            text='Текст для проверки неподписок',
            author=self.user,
        )
        response_unfollow_index = self.authorized_client.get(reverse(
            'posts:follow_index',
        ))
        self.assertNotIn(
            Post.objects.first(),
            response_unfollow_index.context['page_obj'].object_list,
        )

import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTests(TestCase):
    """Проверка форм приложения Posts"""

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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.get(username='author')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_create_post_by_authorized_client(self):
        """Валидная форма создает новый пост авторизованным пользователем."""
        posts_count = Post.objects.count()
        gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=gif,
            content_type='image/gif',
        )
        form_data = {
            'text': 'Уникальный текст для проверки форм',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user},
        ))
        take_post = Post.objects.first()
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(take_post.text, form_data['text'])
        self.assertEqual(take_post.group, self.group)
        self.assertEqual(take_post.author, self.user)
        self.assertEqual(take_post.image.read(), gif)

    def test_edit_post_form_by_atorized_client(self):
        """Валидная форма изменяет пост от авторизованного автора поста"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Изменённый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        take_post = Post.objects.get(id=self.post.id)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id},
        ))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(take_post.text, form_data['text'])
        self.assertEqual(take_post.group, self.group)
        self.assertEqual(take_post.author, self.user)

    def test_add_comment_to_post(self):
        """Валидная форма создаёт комментарий только юзером с регистрацией"""
        count_comments = Comment.objects.count()
        form_data = {'text': 'Test comment'}
        self.authorized_client.post(
            reverse('posts:comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.first().text, form_data['text'])
        self.assertEqual(Comment.objects.count(), count_comments + 1)

    def test_add_comment_to_post(self):
        """Валидная форма не создаёт комментарий незалог-ным пользователем"""
        count_comments = Comment.objects.count()
        form_data = {'text': 'Test comment'}
        self.client.post(
            reverse('posts:comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), count_comments)

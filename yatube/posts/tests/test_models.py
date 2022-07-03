from django.contrib.auth import get_user_model
from django.test import TestCase

from ..constants import MAX_CHAR_LIMIT
from ..models import Group, Post

User = get_user_model()
TEXT_FOR_POST = '''От альянса кочующих гильдий
И до собратства танцующих синти
Одна коалиция сопротивляется
Карцерной матрице тайных полиций
Чему? Пуританству кромешного блага
Чему? Производству, где плавится особь
Мы как дома внутри снежного шара
Тряхнуло слегка — моментально заносит
Эй, старшина, снятся дальние страны?
Зовёт золотое руно?
Значит ты завербован давно
И наш орден берёт тебя в строй
Под своё боевое крыло'''


class PostModelTest(TestCase):
    """Тестирование моделей и их методов"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая сообщество',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEXT_FOR_POST,
            group=cls.group,
        )

    def test_model_post_have_correct_object_names(self):
        """Проверка,  что у модели Post корректно работает __str__."""
        models_str = {
            self.post.text[:MAX_CHAR_LIMIT]: str(self.post),
            self.group.title: str(self.group),
        }
        for name, value in models_str.items():
            with self.subTest(name=name):
                self.assertEqual(name, value)

    def test_verbose_name(self):
        """Проверка verbose_name совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст публикации',
            'author': 'Автор публикации',
            'group': 'Сообщество',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """Проверка help_text совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст вашей публикации',
            'group': 'Выберите сообщество для публикации',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

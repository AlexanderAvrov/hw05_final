from django.contrib.auth import get_user_model
from django.db import models

from .constants import MAX_CHAR_LIMIT
from .validators import validate_not_empty

User = get_user_model()


class Post(models.Model):
    """Модель публикации"""

    text = models.TextField(
        'Текст публикации',
        validators=[validate_not_empty],
        help_text='Введите текст вашей публикации',
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации',
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Сообщество',
        help_text='Выберите сообщество для публикации',
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/',
        blank=True,
        help_text='Загрузите изображение',
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:MAX_CHAR_LIMIT]


class Group(models.Model):
    """Модель сообществ сайта"""

    title = models.CharField('Название сообщества', max_length=200)
    slug = models.SlugField('Адрес страницы сообщества', unique=True)
    description = models.TextField('Описание сообщества')

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Модель комментариев"""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    text = models.TextField(
        'Текст комментария',
        validators=[validate_not_empty],
        help_text='Текст вашего комментария',
    )
    created = models.DateTimeField('Время комментария', auto_now_add=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.text[:MAX_CHAR_LIMIT]


class Follow(models.Model):
    """Модель подписок на авторов"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписаться на',
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'],
            name='unique_follow',
        )]

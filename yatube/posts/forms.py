from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Класс формы для заполнения публикации поста"""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    """Форма заполнения комментария к посту"""

    class Meta:
        model = Comment
        fields = ('text',)

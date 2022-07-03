from django import forms


def validate_not_empty(value):
    """Валидатор на проверку пустое ли поле текста публикации"""
    if value == '':
        raise forms.ValidationError(
            'Это поле необходимо заполнить',
            params={'value': value},
        )

"""
ULID field implementation for Django models.
ULID (Universally Unique Lexicographically Sortable Identifier) используется
вместо UUID, random, стандартных функций Postgres и целочисленных инкрементов.
"""

from django.db import models
from ulid import ULID


def generate_ulid():
    """Генерирует новый ULID."""
    return str(ULID())


class ULIDField(models.CharField):
    """
    Поле для хранения ULID как первичного ключа.
    ULID - это лексикографически сортируемый уникальный идентификатор,
    который содержит временную метку и случайную часть.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 26)
        kwargs.setdefault('default', generate_ulid)
        kwargs.setdefault('editable', False)
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if kwargs.get('max_length') == 26:
            del kwargs['max_length']
        if kwargs.get('default') == generate_ulid:
            del kwargs['default']
        if kwargs.get('editable') is False:
            del kwargs['editable']
        return name, path, args, kwargs

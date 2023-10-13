# flake8: noqa
from django.contrib.auth.models import AbstractUser
from django.db import models

from .configurations import (
    STANDARD_FIELD_VALUE,
    EMAIL_FIELD_VALUE,
)


class Users(AbstractUser):
    """Таблица Пользователей."""

    USER_TEMPLATE = '{}: {}. {}.'
    username = models.CharField(
        'Логин',
        max_length=STANDARD_FIELD_VALUE,
        unique=True,
    )
    first_name = models.CharField(
        'Имя пользователя',
        max_length=STANDARD_FIELD_VALUE,
        blank=True,
    )
    last_name = models.CharField(
        'Фамилия пользователя',
        max_length=STANDARD_FIELD_VALUE,
        blank=True
    )
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=EMAIL_FIELD_VALUE,
        unique=True,
    )

    class Meta:
        ordering = ('last_name', 'first_name', 'username')
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.USER_TEMPLATE.format(
            self.username,
            self.first_name,
            self.last_name
        )


class Subscriptions(models.Model):
    """Таблица отношений Подписок пользователей."""

    SUBSCRIPTIONS_TEMPLATE = '{} > {}'
    # Кто подписался.
    id_subscriber = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='subscriptions_subscriber',
        verbose_name='Кто подписался'
    )
    # На кого подписан.
    id_writer = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='subscriptions_writer',
        verbose_name='На кого подписан'
    )

    class Meta:
        ordering = ['-id_writer']
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Подписки на авторов'
        constraints = [
            models.UniqueConstraint(
                fields=['id_subscriber', 'id_writer'],
                name='unique_id_subscriber_id_writer'
            )
        ]

    def __str__(self):
        return self.SUBSCRIPTIONS_TEMPLATE.format(
            self.id_subscriber,
            self.id_writer,
        )

from django.contrib.auth.models import AbstractUser
from django.db import models

from .users_config import (
    USERNAME_MAX_LENGTH,
    ALLOWED_SYMBOLS_FOR_LOGIN,
    INVALID_WORDS_FOR_LOGIN,
    FIRST_NAME_MAX_LENGTH,
    LAST_NAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
)


class Users(AbstractUser):
    """Таблица Пользователей."""

    class UserRole(models.TextChoices):
        ADMIN = 'admin'
        USER = 'user'
        GUEST = 'guest'

    USER_TEMPLATE = '{}: {} {}'
    username = models.CharField(
        'Логин',
        help_text=(
            'Логин должен быть уникальным не более {} символов, '
            'и может состоять из букв, цифр и следующих символов: {}. '
            'Не допустимо использовать {} в качестве '
            'логина.'.format(
                USERNAME_MAX_LENGTH,
                ALLOWED_SYMBOLS_FOR_LOGIN,
                INVALID_WORDS_FOR_LOGIN,
            )
        ),
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=()
    )

    first_name = models.CharField(
        'Имя пользователя',
        help_text=(
            'Имя пользователя должно быть не более {} '
            'символов'.format(FIRST_NAME_MAX_LENGTH)
        ),
        max_length=FIRST_NAME_MAX_LENGTH,
        blank=True
    )

    last_name = models.CharField(
        'Фамилия пользователя',
        help_text=(
            'Фамилия пользователя должна быть не более {} '
            'символов'.format(LAST_NAME_MAX_LENGTH)
        ),
        max_length=LAST_NAME_MAX_LENGTH,
        blank=True
    )

    email = models.EmailField(
        'Адрес электронной почты',
        help_text=(
            'E-mail должен быть уникальным не более {} '
            'символов'.format(EMAIL_MAX_LENGTH)
        ),
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )

    role = models.CharField(
        'Роль пользователя',
        help_text='Выберите роль для пользователя',
        max_length=max(len(choice) for choice, _ in UserRole.choices),
        choices=UserRole.choices,
        default=UserRole.USER,
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
    """Кто на кого подписан."""
    SUBSCRIPTIONS_TEMPLATE = '{} > {}'

    # Кто подписался.
    id_subscriber = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='id_subscriber',
    )

    # На кого подписан.
    id_writer = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='id_writer',
    )

    def __str__(self):
        return self.SUBSCRIPTIONS_TEMPLATE.format(
            self.id_subscriber,
            self.id_writer,
        )

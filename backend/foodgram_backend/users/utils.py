from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from .users_config import (
    DEFAULT_FROM_EMAIL,
)

CONFIRMATION_CODE_WRONG = {'ОШИБКА': 'Код подтверждения не верный!'}
CONFIRMATION_SUBJECT = 'Код подтверждения для получения токена'
CONFIRMATION_MESSAGE = ('Ваш E-mail был указан для получения токена.\n'
                        'Код подтверждения {}'
                        )


def send_confirmation_code(user, email):
    """Генерирует код подтверждения и отправляет его на указанный E-mail."""
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        CONFIRMATION_SUBJECT,
        CONFIRMATION_MESSAGE.format(confirmation_code),
        DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False
    )

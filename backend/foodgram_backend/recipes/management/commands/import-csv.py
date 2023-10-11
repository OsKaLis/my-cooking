# flake8: noqa
import csv
import os.path

from django.core.management.base import BaseCommand
from django.conf import settings

from recipes.models import (
    Ingredients,
)


class Command(BaseCommand):
    help = 'Импорт данных из CSV в Базу POSTSQL'

    def handle(self, *args, **kwargs):
        self.stdout.write("###   НАЧИНАЮ!   ###")
        patch_full = [
            {'file': 'ingredients.csv', 'obj': Ingredients},
        ]

        for parameter in patch_full:
            patch = os.path.join(
                settings.BASE_DIR,
                'static/data/',
                parameter['file']
            )
            with open(patch, 'r', encoding="utf8") as f_csv:
                reader = csv.reader(f_csv, delimiter=',')
                header = next(reader)
                try:
                    for row in reader:
                        object_dict = {key: value for key, value in zip(
                            header, row)
                        }
                        parameter['obj'].objects.create(**object_dict)
                except ValueError as error:
                    self.stdout.write("Ошибка :{}.".format(error))
            self.stdout.write("Данные модели :{}, ЗАГРУЖЕНА!".format(
                parameter['file'])
            )

        self.stdout.write("###  Готово !!!  ###")

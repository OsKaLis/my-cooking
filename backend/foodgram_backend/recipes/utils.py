# flake8: noqa
import uuid
import os


def get_file_path(instance, filename):
    """Генерациия уникального имени картинки рицепта."""
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('recipes/images/', filename)

# flake8: noqa
from django.db import models
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    RegexValidator
)

from .configurations import (
    MAX_NUMBER,
    MIN_NUMBER,
    DIMENSION_FIELD,
    FIELD_COLOR_DEFAULT,
    DEFAULT_INTERAGER_FIELD,
    MESSAGE_MINEMUM,
    MESSAGE_HIGHS,
)
from users.models import Users


class Tags(models.Model):
    """Таблица TAGS, сортировка по тегу."""

    TAGS_TEMPLATE = '{}: {} {}'
    name = models.CharField(
        'Название сортировки',
        max_length=DIMENSION_FIELD,
    )
    color = models.CharField(
        'Цвет в RGB',
        max_length=FIELD_COLOR_DEFAULT,
        null=True,
        validators=[
            RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Формат для HEX.'
            )
        ]
    )
    slug = models.SlugField(
        'Текс цвета выделения',
        unique=True,
        max_length=DIMENSION_FIELD,
        null=True
    )

    class Meta:
        ordering = ['-slug']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.TAGS_TEMPLATE.format(
            self.name,
            self.color,
            self.slug,
        )


class Ingredients(models.Model):
    """Таблица Ингриндиентов."""

    INGREDIENTS_TEMPLATE = '{} measurement in {}'
    name = models.CharField(
        'Название ингридиента',
        max_length=DIMENSION_FIELD,
    )
    measurement_unit = models.CharField(
        'Измерения ингридиента',
        max_length=DIMENSION_FIELD,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.INGREDIENTS_TEMPLATE.format(
            self.name,
            self.measurement_unit,
        )


class Recipes(models.Model):
    """Рицепт приготовляния блюда."""

    RECIPES_TEMPLATE = '{}: {}'
    tags = models.ManyToManyField(
        Tags,
        through='TagsRecipes',
        verbose_name='Теги'
    )
    author = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        default=DEFAULT_INTERAGER_FIELD,
        related_name='author_recipe',
        verbose_name='Автор рицепта.'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipeIngredients',
        verbose_name='Ингридиенты.',
    )
    name = models.CharField(
        'Название рицепта.',
        max_length=DIMENSION_FIELD,
    )
    image = models.ImageField(
        'Картинка рицепта.',
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    text = models.TextField(
        'Описание',
        default='',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время готовки в минутах.',
        validators=[
            MinValueValidator(MIN_NUMBER),
            MaxValueValidator(MAX_NUMBER)
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации.',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рицепт'
        verbose_name_plural = 'Рицепты'

    def __str__(self):
        return self.RECIPES_TEMPLATE.format(
            self.name,
            self.author,
        )


class TagsRecipes(models.Model):
    """Связь между Тегами и рицептами."""

    TAGSRECIPES_TEMPLATE = '{} > {}'
    id_recipe = models.ForeignKey(
        Recipes,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='id_tr_recept',
        verbose_name='Индификатор рицепта'
    )
    id_teg = models.ForeignKey(
        Tags,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='id_tr_teg',
        verbose_name='Индификатор тега'
    )

    class Meta:
        ordering = ['id_teg']
        verbose_name = 'Рицепт < Тег.'
        verbose_name_plural = 'Рицепты < Теги.'

    def __str__(self):
        return self.TAGSRECIPES_TEMPLATE.format(
            self.id_recipe,
            self.id_teg,
        )


class RecipeIngredients(models.Model):
    """Связь между рицептом и ингридиентами."""

    RECIPEINGREDIENTS_TEMPLATE = '{}: {} ,kol {}'
    id_ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='i_connection_r',
        verbose_name='Индификатор ингридиента.'
    )
    id_recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='r_connection_i',
        verbose_name='Индификатор рицепта.'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество.',
        default=MIN_NUMBER,
        validators=[
            MinValueValidator(MIN_NUMBER, MESSAGE_MINEMUM),
            MaxValueValidator(MAX_NUMBER, MESSAGE_HIGHS)
        ]
    )

    class Meta:
        ordering = ['id_ingredient']
        verbose_name = 'Рицепт < Ингридиент.'
        verbose_name_plural = 'Рицепты < Ингридиенты.'

    def __str__(self):
        return self.RECIPEINGREDIENTS_TEMPLATE.format(
            self.id_recipe,
            self.id_ingredient,
            self.amount,
        )


class Favorited(models.Model):
    """Таблица Избраных рицептов."""

    FAVORITED_TEMPLATE = '{}: {}'
    id_user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        default=DEFAULT_INTERAGER_FIELD,
        related_name='favorited_user',
        verbose_name='Добавил в избранное.'
    )
    id_recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        default=DEFAULT_INTERAGER_FIELD,
        related_name='favorited_recipe',
        verbose_name='Избраный рицепт.'
    )

    class Meta:
        ordering = ['id_user']
        verbose_name = 'Избраный'
        verbose_name_plural = 'Избраные'

    def __str__(self):
        return self.FAVORITED_TEMPLATE.format(
            self.id_user,
            self.id_recipe,
        )


class ShoppingList(models.Model):
    """Таблица Подписок на автора рицептов."""

    SHOPPINGLIST_TEMPLATE = '{}: {}'
    id_user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        default=DEFAULT_INTERAGER_FIELD,
        related_name='shoppinglist_user',
        verbose_name='Добавил в корзину.'
    )
    id_recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        default=DEFAULT_INTERAGER_FIELD,
        related_name='shoppinglist_recipe',
        verbose_name='Рицепт в корзине.'
    )

    class Meta:
        ordering = ['id_user']
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'

    def __str__(self):
        return self.SHOPPINGLIST_TEMPLATE.format(
            self.id_user,
            self.id_recipe,
        )

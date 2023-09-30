from django.db import models
from django.core.validators import MinValueValidator, RegexValidator

from users.models import Users


class Tags(models.Model):
    """Модель TAGS, сортировка по тегу."""

    TAGS_TEMPLATE = '{}: {} {}'
    name = models.CharField(
        'Название сортировки',
        max_length=200,
    )

    color = models.CharField(
        'Цвет в RGB',
        max_length=7,
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
        max_length=200,
        null=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.TAGS_TEMPLATE.format(
            self.name,
            self.color,
            self.slug,
        )


class Ingredients(models.Model):
    """Модель ингриндиентов."""

    INGREDIENTS_TEMPLATE = '{} measurement in {}'
    name = models.CharField(
        'Название ингридиента',
        max_length=200,
    )

    measurement_unit = models.CharField(
        'Измерения ингридиента',
        max_length=200,
    )

    class Meta:
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
        default=0,
        related_name='id_author_recipes',
        verbose_name='Автор рицепта.'
    )

    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipeIngredients',
        verbose_name='Ингридиенты.'
    )

    name = models.CharField(
        'Название рицепта.',
        max_length=200,
    )

    image = models.ImageField(
        'Картинка рицепта.',
        upload_to='recipes/images/',
        null=True,
        blank=True
    )

    text = models.TextField(
        'Описание',
        default='',
    )

    cooking_time = models.IntegerField(
        'Время готовки в минутах.',
        validators=[MinValueValidator(1)]

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
        verbose_name = 'Рицепт < Тег.'
        verbose_name_plural = 'Рицепты < Теги.'

    def __str__(self):
        return self.TAGSRECIPES_TEMPLATE.format(
            self.id_recipe,
            self.id_teg,
        )


class RecipeIngredients(models.Model):
    """Связь между рицептом и ингридиентами."""

    RECIPEINGREDIENTS_TEMPLATE = '{}: {} {}'
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

    amount = models.IntegerField(
        'Количество.',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Рицепт < Ингридиент.'
        verbose_name_plural = 'Рицепты < Ингридиенты.'

    def __str__(self):
        return self.RECIPEINGREDIENTS_TEMPLATE.format(
            self.id_recipe,
            self.id_ingredient,
            self.amount,
        )


class Favorited(models.Model):

    FAVORITED_TEMPLATE = '{}: {}'
    id_user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        default=0,
        related_name='favorited_user_id',
        verbose_name='Добавил в избранное.'
    )

    id_recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        default=0,
        related_name='favorited_recipe_id',
        verbose_name='Избраный рицепт.'
    )

    class Meta:
        verbose_name = "Избраный"
        verbose_name_plural = "Избраные"

    def __str__(self):
        return self.FAVORITED_TEMPLATE.format(
            self.id_user,
            self.id_recipe,
        )


class ShoppingList(models.Model):

    SHOPPINGLIST_TEMPLATE = '{}: {}'
    id_user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        default=0,
        related_name='shoppinglist_user_id',
        verbose_name='Добавил в корзину.'
    )

    id_recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        default=0,
        related_name='shoppinglist_recipe_id',
        verbose_name='Рицепт в корзине.'
    )

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзина"

    def __str__(self):
        return self.SHOPPINGLIST_TEMPLATE.format(
            self.id_user,
            self.id_recipe,
        )

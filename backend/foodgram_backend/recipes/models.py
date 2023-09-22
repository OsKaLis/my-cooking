from django.db import models

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
    )

    slug = models.SlugField(
        'Текс цвета выделения',
        unique=True,
        max_length=200,
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
    name_recipe = models.CharField(
        'Название рицепта',
        max_length=200,
    )

    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None
    )

    text = models.TextField(
        default='',
        blank=True
    )

    cooking_time = models.IntegerField()

    id_author = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='id_author',
    )

    tags = models.ManyToManyField(Tags, through='TagsRecipes')

    ingredients = models.ManyToManyField(Ingredients,
                                         through='RecipeIngredients')

    pub_date = models.DateTimeField(
        verbose_name='Дата',
        auto_now_add=True,
    )

    # is_favorited =
    # is_in_shopping =

    class Meta:
        verbose_name = 'Рицепт'
        verbose_name_plural = 'Рицепты'

    def __str__(self):
        return self.RECIPES_TEMPLATE.format(
            self.name_recipe,
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
    )
    id_teg = models.ForeignKey(
        Tags,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='id_tr_teg',
    )

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
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='id_ri_ingredient',
    )

    id_recipe = models.ForeignKey(
        Recipes,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='id_ri_recept',
    )

    amount = models.IntegerField()

    def __str__(self):
        return self.RECIPEINGREDIENTS_TEMPLATE.format(
            self.id_recipe,
            self.id_ingredient,
            self.amount,

        )


class UsernameRecipesModel(models.Model):
    """Абстрактный клас для Список покупок и на избраный рицепт"""

    TEMPLATE = '{}: {}'
    id_user = models.ForeignKey(
        Users,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        # related_name='id_ur_user',
    )

    id_recipe = models.ForeignKey(
        Recipes,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        # related_name='id_ur_recept',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.TEMPLATE.format(
            self.id_user,
            self.id_recipe,
        )


class Favorited(UsernameRecipesModel):
    class Meta:
        verbose_name = "Любимый"
        verbose_name_plural = "Любимые"


class ShoppingList(UsernameRecipesModel):
    class Meta:
        verbose_name = "Покупка"
        verbose_name_plural = "Покупки"

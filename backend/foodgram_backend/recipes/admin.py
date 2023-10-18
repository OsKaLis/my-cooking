# flake8: noqa
from django.contrib import admin

from recipes.models import (
    Tags,
    Ingredients,
    Recipes,
    TagsRecipes,
    RecipeIngredients,
    Favorited,
    ShoppingList,
)


class TagsPanel(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    list_editable = (
        'name',
        'color',
        'slug'
    )
    empty_value_display = '_пусто_'


class IngredientsPanel(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    list_filter = ('name', )
    search_fields = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredients
    min_num = 1

class RecipesTags(admin.TabularInline):
    model = TagsRecipes
    min_num = 1


class RecipesPanel(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'author',
        'count_favorites',
    )
    list_editable = (
        'name',
        'author'
    )
    inlines = (RecipeIngredientInline, RecipesTags)
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'

    def count_favorites(self, obj):
        return obj.favorited_recipe.count()


class TagsRecipesPanel(admin.ModelAdmin):
    list_display = (
        'pk',
        'id_recipe',
        'id_teg',
    )
    list_editable = (
        'id_recipe',
        'id_teg',
    )


class RecipeIngredientsPanel(admin.ModelAdmin):
    list_display = (
        'pk',
        'id_ingredient',
        'id_recipe',
        'amount'
    )
    list_editable = (
        'id_ingredient',
        'id_recipe',
        'amount'
    )


class FavoritedPanel(admin.ModelAdmin):
    list_display = (
        'pk',
        'id_user',
        'id_recipe',
    )
    list_editable = (
        'id_user',
        'id_recipe',
    )


class ShoppingListPanel(admin.ModelAdmin):
    list_display = (
        'pk',
        'id_user',
        'id_recipe',
    )
    list_editable = (
        'id_user',
        'id_recipe',
    )


admin.site.register(Tags, TagsPanel)
admin.site.register(Ingredients, IngredientsPanel)
admin.site.register(Recipes, RecipesPanel)
admin.site.register(TagsRecipes, TagsRecipesPanel)
admin.site.register(RecipeIngredients, RecipeIngredientsPanel)
admin.site.register(Favorited, FavoritedPanel)
admin.site.register(ShoppingList, ShoppingListPanel)

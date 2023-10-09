from django_filters.rest_framework import (
    FilterSet,
    CharFilter,
    BooleanFilter,
    ModelMultipleChoiceFilter
)
from rest_framework import filters
from recipes.models import Recipes

from recipes.models import Tags


class DynamicSearchFilter(filters.SearchFilter):
    """Динамически поиск для ингридиентов."""
    search_param = 'name'

    def get_search_fields(self, view, request):
        if request.query_params.get('name'):
            return ['name']
        return super().get_search_fields(view, request)


class RecipesFilter(FilterSet):
    """Фильтр по автору, избраным рицептам, в корзине, тегам."""

    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tags.objects.all()
    )

    author = CharFilter(field_name='author__id')
    is_favorited = BooleanFilter(method='method_favorited_filter')
    is_in_shopping_cart = BooleanFilter(method='method_shopping_filter')

    class Meta:
        model = Recipes
        fields = [
            'is_favorited',
            'author',
            'is_in_shopping_cart',
            'tags',
        ]

    def method_favorited_filter(self, queryset, name, value):
        user = self.request.user
        print(value)
        if value and user.is_authenticated:
            return queryset.filter(favorited_recipe__id_user=user)
        return queryset

    def method_shopping_filter(self, queryset, name, value):
        user = self.request.user
        print(value)
        if value and user.is_authenticated:
            return queryset.filter(shoppinglist_recipe__id_user=user)
        return queryset

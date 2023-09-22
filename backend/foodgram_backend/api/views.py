# from django.shortcuts import render
from rest_framework import viewsets
from recipes.models import (
    Ingredients,
    Tags,
)
from api.serializers import (
    IngredientsSerializer,
    TagsSerializer,
)

from rest_framework import filters


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None


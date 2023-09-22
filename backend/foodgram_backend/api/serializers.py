# import datetime as dt
from rest_framework import serializers
import webcolors

from recipes.models import (
    Ingredients,
    Tags,
)


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')

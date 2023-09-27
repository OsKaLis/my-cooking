# import datetime as dt
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from recipes.models import (
    Ingredients,
    Tags,
    Users,
    Recipes,
)


class UsersSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, User):
        return False


class UsersCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        user = Users(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UsersPatchSerializer(serializers.Serializer):
    model = Users

    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientsSerializer(serializers.Serializer):
    # id = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    id = IngredientsSerializer()
    amount = serializers.IntegerField()


class TagsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class RecipesSerializer(serializers.ModelSerializer):
    tags = SlugRelatedField(
        slug_field='id',
        many=True,
        read_only=False,
        queryset=Tags.objects.all()
    )
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    # ingredients = RecipeIngredientsSerializer(many=True, read_only=True)

    class Meta:
        model = Recipes
        fields = (
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'author',
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


"""
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipes = Recipes.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            RecipeIngredientsSerializer.objects.create(
                recipes=recipes,
                **ingredient_data
            )
        return recipes



    def create(self, validated_data):
        if 'ingredients' not in self.initial_data:
            recipe = Recipes.objects.create(**validated_data)
            return recipe
        else:
            ingredients_data = validated_data.pop('ingredients')
            recipe = Recipes.objects.create(**validated_data)
            for ingredient_data in ingredients_data:
                ingredient, status = Ingredients.objects.get_or_create(
                    **ingredient_data
                )
                RecipeIngredients.objects.create(
                    ingredient_data=ingredient,
                    recipe=recipe
                )
            return recipe
"""


class RecipesListRetrieveSerializer(RecipesSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UsersSerializer()
    tags = TagsSerializer(many=True)

    class Meta:
        model = Recipes
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, User):
        return False

    def get_is_in_shopping_cart(self, User):
        return False

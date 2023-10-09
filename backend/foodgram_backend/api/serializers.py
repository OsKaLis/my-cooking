import base64

from django.shortcuts import get_object_or_404
from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Ingredients,
    RecipeIngredients,
    Tags,
    Recipes,
    Favorited,
    ShoppingList,
)
from users.models import (
    Users,
    Subscriptions,
)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UsersSerializer(serializers.ModelSerializer):
    """Вывои информации об Пользователях."""
    is_subscriber = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Users
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscriber',
        )

    def get_queryset(self):
        return Users.objects.all()

    def get_is_subscriber(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscriptions.objects.filter(
            id_subscriber=request.user.id,
            id_writer=obj.id,
        ).exists()


class UsersCreateSerializer(serializers.ModelSerializer):
    """Создание пользователя."""
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


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля."""
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class IngredientsSerializer(serializers.ModelSerializer):
    """Показ ингридиентов."""

    class Meta:
        model = Ingredients
        fields = ('id', 'name', 'measurement_unit')


class TagsSerializer(serializers.ModelSerializer):
    """Показ тегов."""

    class Meta:
        model = Tags
        fields = ('id', 'name', 'color', 'slug')


class AddRecipeIngredientsSerializer(serializers.ModelSerializer):
    """Для записи ингридиентов."""

    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount', )


class RecipesSerializer(serializers.ModelSerializer):
    """Для записи рицепта."""

    tags = SlugRelatedField(
        slug_field='id',
        many=True,
        read_only=False,
        queryset=Tags.objects.all()
    )
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    ingredients = AddRecipeIngredientsSerializer(
        many=True,
    )
    image = Base64ImageField(required=False, allow_null=True)

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

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipes = Recipes.objects.create(**validated_data)
        recipes.tags.set(tags_data)

        for ingredient_data in ingredients_data:
            amount_data = ingredient_data.get('amount')
            id_ingredient_data = ingredient_data['id']
            ingredient = get_object_or_404(Ingredients, pk=id_ingredient_data)
            RecipeIngredients.objects.create(
                id_recipe=recipes,
                id_ingredient=ingredient,
                amount=amount_data
            )

        return recipes

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')

        RecipeIngredients.objects.filter(
                id_recipe=instance,
                id_ingredient__in=instance.ingredients.all()
        ).delete()

        instance.tags.set(tags_data)

        for ingredient_data in ingredients_data:
            amount_data = ingredient_data.get('amount')
            id_ingredient_data = ingredient_data['id']
            ingredient = get_object_or_404(Ingredients, pk=id_ingredient_data)
            RecipeIngredients.objects.create(
                    id_recipe=instance,
                    id_ingredient=ingredient,
                    amount=amount_data
                )

        instance.save()
        return instance


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Показ ингридиентов в рицепте."""

    id = serializers.ReadOnlyField(source='id_ingredient.id')
    name = serializers.ReadOnlyField(source='id_ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='id_ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipesListRetrieveSerializer(serializers.ModelSerializer):
    """Для вывода рицепта."""

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UsersSerializer()
    tags = TagsSerializer(many=True)
    ingredients = serializers.SerializerMethodField()

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

    def get_ingredients(self, obj):
        all_user = RecipeIngredients.objects.filter(id_recipe=obj.id)
        serializer = RecipeIngredientsSerializer(
            all_user,
            many=True,
            read_only=True,
        )
        return serializer.data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorited.objects.filter(
            id_user=request.user.id,
            id_recipe=obj,
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingList.objects.filter(
            id_user=request.user.id,
            id_recipe=obj,
        ).exists()


class RecipesSubscriptionsSerializer(serializers.ModelSerializer):
    """Показ рицепт в подписках."""

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Мои подписки."""
    email = serializers.ReadOnlyField(source='id_writer.email')
    id = serializers.ReadOnlyField(source='id_writer.id')
    username = serializers.ReadOnlyField(source='id_writer.username')
    first_name = serializers.ReadOnlyField(source='id_writer.first_name')
    last_name = serializers.ReadOnlyField(source='id_writer.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscriptions
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscriptions.objects.all(),
                fields=('id_subscriber', 'id_writer')
            )
        ]

    def validate_username(self, value):
        if self.context.get('request').user == value:
            raise serializers.ValidationError(
                'Нельза подписываться на самого себя.')
        return value

    def get_recipes_count(self, obj):
        return Recipes.objects.filter(author=obj.id_writer).count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return bool(Subscriptions.objects.filter(
            id_subscriber=request.user.id,
            id_writer=obj.id_writer.id,
        ))

    def get_recipes(self, obj):
        all_user = Recipes.objects.filter(author=obj.id_writer)[:3]
        serializer = RecipesSubscriptionsSerializer(
            all_user,
            many=True,
            read_only=True,
        )
        return serializer.data


class InSubscriptionsSerializer(serializers.Serializer):
    """Я только что подписался."""
    email = serializers.ReadOnlyField()
    id = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return bool(Subscriptions.objects.filter(
            id_subscriber=request.user.id,
            id_writer=obj.id,
        ))

    def get_recipes(self, obj):
        all_user = Recipes.objects.filter(author=obj.id)
        serializer = RecipesSubscriptionsSerializer(
            all_user,
            many=True,
            read_only=True,
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipes.objects.filter(author=obj.id).count()


class RecipesReductionSerializer(serializers.Serializer):
    """Показ сокращёный рицепт."""
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipes
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

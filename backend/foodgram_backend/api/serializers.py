# flake8: noqa
import base64

from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from recipes.models import (
    Ingredients,
    RecipeIngredients,
    Recipes,
    Tags
)
from users.models import Subscriptions, Users
from recipes.configurations import (
    MIN_NUMBER,
    MAX_NUMBER,
    WITHDRAWAL_CALL_RECIPES
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

    def get_is_subscriber(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.subscriptions_subscriber.filter(
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
    
    def validate_current_password(self, value):
        validate_password(value)
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] == attrs['current_password']:
            raise serializers.ValidationError(
                {'detail': ['Старый пароль такойже как и прежний.']}
            )
        return super().validate(attrs)


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
    """
    # В сериализаторе не получается так сделать :(
    # ругается на amount, считайте эта ошибкой  
    amount = serializers.IntegerField(
        min_value=MIN_NUMBER,
        max_value=MAX_NUMBER,
    )
    """
    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')
    
    def to_internal_value(self, data):
        if data['amount'] < MIN_NUMBER:
            raise serializers.ValidationError(
                {'detail': ['Ингридиентов не должно быть меньше 1.']})
        if data['amount'] > MAX_NUMBER:
            raise serializers.ValidationError(
                {'detail': ['Ингридиентов слишком много.']})
        return super().to_internal_value(data)


class RecipesSerializer(serializers.ModelSerializer):
    """Для записи рицепта."""
    
    ingredients = AddRecipeIngredientsSerializer(
        many=True,
    )
    tags = SlugRelatedField(
        slug_field='id',
        many=True,
        read_only=False,
        queryset=Tags.objects.all()
    )
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    image = Base64ImageField(required=False, allow_null=True)
    cooking_time = serializers.IntegerField(
        min_value=MIN_NUMBER,
        max_value=MAX_NUMBER,
    )

    class Meta:
        model = Recipes
        fields = (
            'ingredients',
            'tags',
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
        RecipeIngredients.objects.bulk_create(
            [RecipeIngredients(
                id_recipe=recipes,
                id_ingredient=get_object_or_404(Ingredients, pk=ingredient_data['id']),
                amount=ingredient_data.get('amount')) for ingredient_data in ingredients_data
            ],
            batch_size=None
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
        instance.r_connection_i.filter(
            id_ingredient__in=instance.ingredients.all()
        ).delete()
        instance.tags.set(tags_data)
        RecipeIngredients.objects.bulk_create(
            [RecipeIngredients(
                id_recipe=instance,
                id_ingredient=get_object_or_404(Ingredients, pk=ingredient_data['id']),
                amount=ingredient_data.get('amount')) for ingredient_data in ingredients_data
            ],
            batch_size=None
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
        ingredients_recipe = obj.r_connection_i.filter()
        serializer = RecipeIngredientsSerializer(
            ingredients_recipe,
            many=True,
            read_only=True,
        )
        return serializer.data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.favorited_recipe.filter(id_user=request.user.id).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.shoppinglist_recipe.filter(id_user=request.user.id).exists()


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


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Подписки пользователя."""
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

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.id_subscriber.subscriptions_subscriber.filter(
            id_writer=obj.id_writer
        ).exists()
        
    def get_recipes(self, obj):
        recipes = obj.id_writer.author_recipe.filter(
            )[:WITHDRAWAL_CALL_RECIPES]
        serializer = RecipesReductionSerializer(
            recipes,
            many=True,
            read_only=True,
        )
        return serializer.data
    
    def get_recipes_count(self, obj):
        return obj.id_writer.author_recipe.filter().count()
        

class AddSubscriptionsSerializer(serializers.Serializer):
    """Проверка на добавление в подписки."""
    subscriber = serializers.IntegerField(required=True)
    writer = serializers.IntegerField(required=True)
    
    def validate(self, attrs):
        subscriber = get_object_or_404(Users, pk=attrs['subscriber'])
        writer = get_object_or_404(Users, pk=attrs['writer'])
        if writer.subscriptions_writer.filter(id_subscriber=subscriber):
            raise serializers.ValidationError(
                {'detail': ['Выуже подписаны на этого автора.']}
            )
        if attrs['subscriber'] == attrs['writer']:
            raise serializers.ValidationError(
                {'detail': ['Нельза подписываться на самого себя.']}
            )
        return super().validate(attrs)

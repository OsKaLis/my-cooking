from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from recipes.models import (
    Ingredients,
    Tags,
    Recipes,
)
from users.models import (
    Users,
    Subscriptions,
)


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


class RecipeIngredientsSerializer(serializers.Serializer):
    # id = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    id = IngredientsSerializer()
    amount = serializers.IntegerField()


class TagsSerializer(serializers.ModelSerializer):
    """Показ тегов."""

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
        all_user = Recipes.objects.filter(author=obj.id_writer)
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

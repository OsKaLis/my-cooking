# flake8: noqa
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorited, Ingredients, RecipeIngredients, Recipes,
                            ShoppingList, Tags)
from rest_framework import filters, mixins, status, viewsets
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Subscriptions, Users
from api.serializers import (
    IngredientsSerializer,
    InSubscriptionsSerializer,
    RecipesListRetrieveSerializer,
    RecipesReductionSerializer,
    RecipesSerializer,
    SetPasswordSerializer,
    SubscriptionsSerializer,
    TagsSerializer,
    UsersCreateSerializer,
    UsersSerializer
)
from .filters import DynamicSearchFilter, RecipesFilter
from .permissions import IsAdminUserOrReadOnly, ProfileReadOnly


class UsersViewSet(viewsets.ModelViewSet):
    """Создание пользователя или просмотр."""
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (ProfileReadOnly, )

    def get_serializer_class(self):
        if self.action in ['create', ]:
            return UsersCreateSerializer
        return UsersSerializer


class ProfileUserView(APIView):
    """Показывает текущего пользователя."""
    def get(self, request):
        serializer = UsersSerializer(
            get_object_or_404(Users, pk=request.user.id)
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class SetPasswordView(APIView):
    """Изменение пароля текущего пользователя."""
    permission_classes = (IsAuthenticated, )

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = SetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            current_password = serializer.data.get("current_password")
            new_password = serializer.data.get("new_password")
            if current_password == new_password:
                return Response(
                    {"detail": ["Старый пароль такойже как и прежний."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not self.object.check_password(current_password):
                return Response(
                    {"detail": ["Старый пароль неверный."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionsViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Показывает подписки текущего пользователя."""
    serializer_class = SubscriptionsSerializer

    def get_queryset(self):
        return self.request.user.subscriber.all()


class SubscriberWriterView(APIView):
    """Добавление в подписки или удаление."""

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(Users, pk=self.kwargs.get('pk'))
        if self.request.user == user:
            return Response(
                {"detail": ["Нельзя подписываться на самого себя."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Subscriptions.objects.filter(
            id_subscriber=self.request.user,
            id_writer=user
        ):
            return Response(
                {"detail": ["Выуже подписаны на этого автора."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscriptions.objects.create(
            id_subscriber=self.request.user,
            id_writer=user
        )
        serializer = InSubscriptionsSerializer(
            user,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, format=None):
        user = get_object_or_404(Users, pk=self.kwargs.get('pk'))
        subscription = Subscriptions.objects.filter(
            id_subscriber=self.request.user,
            id_writer=user
        )
        if not subscription:
            return Response(
                {"detail": ["Вы уже отписались или не подписывались."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagsViewSet(viewsets.ModelViewSet):
    """Работа с тегами."""
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsAdminUserOrReadOnly, )
    pagination_class = None


class IngredientsViewSet(viewsets.ModelViewSet):
    """Работа с ингридиентами."""
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = (IsAdminUserOrReadOnly, )
    pagination_class = None
    filter_backends = [DynamicSearchFilter, filters.SearchFilter]
    search_fields = ['^name', ]


class RecipesViewSet(viewsets.ModelViewSet):
    """Обработка запросов для Рицепта."""
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return RecipesListRetrieveSerializer
        return RecipesSerializer


class FavoritedView(APIView):
    """Добавляем или удаляем из избранного."""

    def post(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipes, pk=self.kwargs.get('pk'))
        if Favorited.objects.filter(
            id_user=self.request.user,
            id_recipe=recipe
        ):
            return Response(
                {"detail": ["На этот рицепт вы уже подписаны."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorited.objects.create(
            id_user=self.request.user,
            id_recipe=recipe
        )
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, pk, format=None):
        recipe = get_object_or_404(Recipes, pk=self.kwargs.get('pk'))
        favorited = Favorited.objects.filter(
            id_user=self.request.user,
            id_recipe=recipe
        )
        if not favorited:
            return Response(
                {"detail": ["Рицепт нет в избраном."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorited.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCartView(APIView):
    """Скачать список ингридиентов для покупок."""

    def get(self, request):
        user = self.request.user
        ingredients = RecipeIngredients.objects.filter(
            id_recipe__shoppinglist_recipe__id_user=user
        ).values_list(
            'id_ingredient__name',
            'id_ingredient__measurement_unit',
        ).annotate(amount=Sum('amount')).order_by()
        filename = 'Список_к_покупки_ингридиентов.txt'
        shoppingList = 'Список ингридиентов:\n\n'
        for ing in ingredients:
            shoppingList += f'{ing[0]}: {ing[2]} {ing[1]}\n'
        response = HttpResponse(
            shoppingList,
            content_type='text/plain'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


class AddCartView(APIView):
    """Добавить или удалить из корзины."""

    def post(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipes, pk=self.kwargs.get('pk'))
        if ShoppingList.objects.filter(
            id_user=self.request.user,
            id_recipe=recipe
        ):
            return Response(
                {"detail": ["Выуже добавии этот рицепт."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingList.objects.create(
            id_user=self.request.user,
            id_recipe=recipe
        )
        serializer = RecipesReductionSerializer(
            recipe,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, format=None):
        recipe = get_object_or_404(Recipes, pk=self.kwargs.get('pk'))
        shoppingList = ShoppingList.objects.filter(
            id_user=self.request.user,
            id_recipe=recipe
        )
        if not shoppingList:
            text = "Вы уже удалиле рицепт из корзины или не добавляли."
            return Response(
                {"detail": [text]},
                status=status.HTTP_400_BAD_REQUEST
            )
        shoppingList.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

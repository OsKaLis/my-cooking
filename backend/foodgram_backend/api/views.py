from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, status, mixins
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    # AllowAny,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from recipes.models import (
    Ingredients,
    Tags,
    Recipes,
    Favorited,
)
from api.serializers import (
    IngredientsSerializer,
    TagsSerializer,
    UsersSerializer,
    UsersCreateSerializer,
    SetPasswordSerializer,
    SubscriptionsSerializer,
    RecipesSerializer,
    RecipesListRetrieveSerializer,
    InSubscriptionsSerializer,


)
from .permissions import (
    AuthenticatedOrReadOnly,
    IsAdminUserOrReadOnly,
)
from users.models import (
    Users,
    Subscriptions,
)


class UsersViewSet(viewsets.ModelViewSet):
    """Создание пользователя или просмотр."""
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (AuthenticatedOrReadOnly, )

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
    """Мои подписки."""
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
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    # permission_classes = (AllowAny,)

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

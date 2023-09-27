from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from recipes.models import (
    Ingredients,
    Tags,
    Users,
    Recipes,
)
from api.serializers import (
    IngredientsSerializer,
    TagsSerializer,
    UsersSerializer,
    UsersCreateSerializer,
    UsersPatchSerializer,
    RecipesSerializer,
    RecipesListRetrieveSerializer,
)


class UserLoginView(ObtainAuthToken):
    """Получения токена."""

    def post(self, request, *args, **kwargs):

        email = request.data['email']
        user = Users.objects.get(email=email)
        request.data['username'] = user.username
        del request.data['email']

        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    # permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return RecipesListRetrieveSerializer
        return RecipesSerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    # permission_classes = (CreateUsers,)
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action in ['create', ]:
            return UsersCreateSerializer
        return UsersSerializer


class CurrentUserView(APIView):
    """Показывает текущего пользователя."""
    # permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        serializer = UsersSerializer(
            get_object_or_404(Users, username=request.user.username)
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """Смена пароля."""
    # permission_classes = (ChangePasswordUsers,)
    permission_classes = (IsAuthenticated, )

    def get_object(self, queryset=None):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = UsersPatchSerializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.data.get("current_password")
            if not self.object.check_password(old_password):
                return Response({"current_password": ["Wrong password."]},
                                status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

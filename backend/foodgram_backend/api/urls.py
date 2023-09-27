from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()
router.register(
    r'ingredients',
    views.IngredientsViewSet,
    basename='Ingredients'
)
router.register(
    r'tags',
    views.TagsViewSet,
    basename='Tags'
)
router.register(
    r'users',
    views.UsersViewSet,
    basename='Users'
)
router.register(
    r'recipes',
    views.RecipesViewSet,
    basename='Recipes'
)

urlpatterns = [
    path('users/me/', views.CurrentUserView.as_view()),
    path('users/set_password/', views.ChangePasswordView.as_view()),
    path('auth/token/login/', views.UserLoginView.as_view()),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]

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
    r'users/subscriptions',
    views.SubscriptionsViewSet,
    basename='Users'
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
    path('users/me/', views.ProfileUserView.as_view()),
    path('users/set_password/', views.SetPasswordView.as_view()),
    path('users/<int:pk>/subscribe/', views.SubscriberWriterView.as_view()),
    path('recipes/<int:pk>/favorite/', views.FavoritedView.as_view()),
    path('recipes/<int:pk>/shopping_cart/', views.AddCartView.as_view()),
    path('recipes/download_shopping_cart/',
         views.DownloadShoppingCartView.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

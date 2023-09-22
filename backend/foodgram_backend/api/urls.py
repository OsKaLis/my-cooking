from django.urls import include, path
from rest_framework import routers

from api.views import (
    IngredientsViewSet,
    TagsViewSet,
)

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'ingredients', IngredientsViewSet)
router.register(r'tags', TagsViewSet)

urlpatterns = [
     path('', include(router.urls)),
]

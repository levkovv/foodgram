from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (DownloadShoppingCartViewSet, FavoriteRecipesViewSet,
                    IngredientViewSet, RecipeViewSet, ShoppingCartViewSet,
                    SubscribeListViewSet, SubscribeViewSet, TagViewSet)

router = DefaultRouter()
router.register(
    r'users/(?P<user_id>\d+)/subscribe', SubscribeViewSet)
router.register(
    r'users/subscriptions', SubscribeListViewSet, basename='subscribe_list')
router.register(
    r'tags', TagViewSet)
router.register(
    r'ingredients', IngredientViewSet)
router.register(
    r'recipes/download_shopping_cart', DownloadShoppingCartViewSet)
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteRecipesViewSet, basename='add_to_favorite')
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet, basename='add_to_shopping_cart')
router.register(
    r'recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken')),
]

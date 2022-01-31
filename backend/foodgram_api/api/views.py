from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from users.models import Follow, User
from .filters import IngredientSearchFilter, RecipeFilter
from .mixins import AddAndDeleteMixin
from .models import FavoriteRecipe, Ingredient, Recipe, ShoppingCart, Tag
from .pagination import CustomPageNumberPagination
from .serializers import (DownloadShoppingCartSerializer,
                          FavoriteRecipesSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class FavoriteRecipesViewSet(AddAndDeleteMixin, viewsets.ModelViewSet):
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteRecipesSerializer
    model_class = FavoriteRecipe


class ShoppingCartViewSet(AddAndDeleteMixin, viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    model_class = ShoppingCart


class DownloadShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = DownloadShoppingCartSerializer
    queryset = ShoppingCart.objects.all()

    def get_ingredients_result_string(self, recipes_from_shopping_cart):
        content = ''
        recipe_ingredients = recipes_from_shopping_cart.values_list(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit').annotate(
                total=Sum('recipe__ingredients_from_recipe__amount'))
        for ingredient in recipe_ingredients:
            content += f'{ingredient[0]} {ingredient[2]} {ingredient[1]}\n'
        return content

    def list(self, request, *args, **kwargs):
        user = request.user
        recipes_from_shopping_cart = ShoppingCart.objects.filter(
            user=user)
        content = self.get_ingredients_result_string(
            recipes_from_shopping_cart)
        headers = {
                'Content-Type': 'text/plain',
                'Content-Disposition':
                'attachment; filename="shopping_cart.txt"'
            }
        return HttpResponse(
            content, headers=headers
        )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeReadSerializer
        return RecipeWriteSerializer


class SubscribeViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeSerializer
    queryset = Follow.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('post', 'delete')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        author = get_object_or_404(
            User, id=kwargs['user_id']
        )
        serializer.save(
            user=user,
            author=author
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        user = request.user
        author = get_object_or_404(User, id=user_id)
        get_object_or_404(
            Follow,
            user=user,
            author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscribeListViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

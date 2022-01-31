from django.shortcuts import get_object_or_404
from django_filters import filters
from django_filters.rest_framework import FilterSet
from rest_framework.filters import SearchFilter

from users.models import User
from .models import Recipe, Tag


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    author = filters.NumberFilter(method='filter_author')
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags',)

    def filter_author(self, queryset, name, value):
        if value:
            author = get_object_or_404(User, id=value)
            return queryset.filter(author=author)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        if value == 1:
            return self.request.user.favorite_recipes.all()
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == 1:
            return self.request.user.shopping_cart_recipes.all()
        return queryset

from django.contrib import admin

from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class IngredientsInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'amount_of_adding_to_favorite')
    list_filter = ('author', 'name', 'tags')
    inlines = (IngredientsInLine,)

    def amount_of_adding_to_favorite(self, obj):
        count = FavoriteRecipe.objects.filter(recipe=obj).count()
        return count


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(FavoriteRecipe)
admin.site.register(RecipeIngredient)
admin.site.register(ShoppingCart)

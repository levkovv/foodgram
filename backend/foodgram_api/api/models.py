from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField('Ингредиент', max_length=254)
    measurement_unit = models.CharField('Единицы измерения', max_length=10)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('Название тэга', max_length=200)
    color = ColorField('Цвет в HEX-формате', null=True)
    slug = models.SlugField('Слаг', unique=True, null=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, verbose_name='Автор', related_name='recipes',
        on_delete=models.CASCADE)
    name = models.CharField('Название рецепта', max_length=200)
    text = models.TextField('Описание рецепта')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(
            1, 'Время приготовления не может быть меньше 1')])
    image = models.ImageField('Картинка')
    tags = models.ManyToManyField(
        Tag, verbose_name='Тэги')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Необходимые ингредиенты')
    date_of_creation = models.DateTimeField(
        'Дата и время создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-date_of_creation',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredients_from_recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField(
        'Количество ингредиета',
        validators=[MinValueValidator(
            1, 'Количество ингредиента не может быть меньше 1')])

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = (models.UniqueConstraint(
            fields=('recipe', 'ingredient'),
            name='unique_recipe_ingredient'),
        )

    def __str__(self):
        return (
            f'{self.ingredient} {self.amount}'
            f'{self.ingredient.measurement_unit}'
        )


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь',
        related_name='favorite_user_recipes'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (models.UniqueConstraint(
            fields=('user', 'recipe'),
            name='unique_recipe_in_favorites'),
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь',
        related_name='shopping_cart_user_recipes'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (models.UniqueConstraint(
            fields=('user', 'recipe'),
            name='unique_recipe_in_shopping_cart'),
        )

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        unique=True, max_length=254,
        verbose_name='email')
    username = models.CharField(
        unique=True, max_length=150,
        verbose_name='Имя пользователя')
    first_name = models.CharField(
        max_length=150, verbose_name='Имя')
    last_name = models.CharField(
        max_length=150, verbose_name='Фамилия')
    password = models.CharField(
        max_length=150, verbose_name='Пароль')
    favorite_recipes = models.ManyToManyField(
        to='api.Recipe', through='api.FavoriteRecipe',
        related_name='user_favorite_recipes',
        verbose_name='Избранные рецепты'
    )
    shopping_cart_recipes = models.ManyToManyField(
        to='api.Recipe', through='api.ShoppingCart',
        related_name='user_shopping_cart',
        verbose_name='Список покупок'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
        verbose_name='Подписчик'
        )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        verbose_name='Автор'
    )

    class Metа:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(fields=('user', 'author'),
                                    name='unique_followers'),
        )

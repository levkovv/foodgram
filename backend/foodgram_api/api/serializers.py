from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.models import Follow, User
from users.serializers import UserSerializer
from .models import (FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class FavoriteRecipesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(
        read_only=True, source='recipe.name')
    image = serializers.ImageField(
        use_url=True, read_only=True, source='recipe.image')
    cooking_time = serializers.CharField(
        read_only=True, source='recipe.cooking_time')

    class Meta:
        model = FavoriteRecipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        recipe = get_object_or_404(Recipe, id=data['id'])
        if FavoriteRecipe.objects.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное')
        return super().validate(data)


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(
        read_only=True, source='recipe.name')
    image = serializers.ImageField(
        read_only=True, source='recipe.image')
    cooking_time = serializers.CharField(
        read_only=True, source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        recipe = get_object_or_404(Recipe, id=data['id'])
        if ShoppingCart.objects.filter(recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок')
        return super().validate(data)


class DownloadShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        read_only=True, source='ingredient.id')
    name = serializers.CharField(
        read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True, source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    image = Base64ImageField()
    author = UserSerializer(
        required=False, read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True, source='ingredients_from_recipe',
        read_only=True)
    tags = TagSerializer(
        many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = (
            'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class AddIngredient(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(
        required=False, read_only=True)
    ingredients = AddIngredient(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = ('id', 'is_favorited', 'is_in_shopping_cart')

    def validate(self, data):
        user = self.context['request'].user
        recipe_id = data.get('id')
        if recipe_id:
            recipe = get_object_or_404(Recipe, id=recipe_id)
            if user != recipe.author:
                raise serializers.ValidationError(
                    'Нельзя редактировать чужой рецепт')
        ingredients = data.get('ingredients')
        for ingredient in ingredients:
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть меньше 1')
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError(
                    'Выберите хотя бы один тэг')
        data.update({'ingredients': ingredients})
        data.update({'tags': tags})
        return super().validate(data)

    def save_tags_and_ingredients(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        recipe.tags.set(tags)
        ingredients = validated_data.pop('ingredients')
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

    def create(self, validated_data):
        user = self.context['request'].user
        recipe = Recipe.objects.create(
            author=user,
            name=validated_data['name'],
            text=validated_data['text'],
            cooking_time=validated_data['cooking_time'],
            image=validated_data['image'],
        )
        self.save_tags_and_ingredients(recipe, validated_data)
        return recipe

    def update(self, instance, validated_data):
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.save_tags_and_ingredients(instance, validated_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data


class SubscribeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    email = serializers.EmailField(
        read_only=True, source='author.email')
    username = serializers.CharField(
        read_only=True, source='author.username')
    first_name = serializers.CharField(
        read_only=True, source='author.first_name')
    last_name = serializers.CharField(
        read_only=True, source='author.last_name')
    is_subscribe = serializers.SerializerMethodField(
        read_only=True)
    recipes = serializers.SerializerMethodField(
        read_only=True)
    recipes_count = serializers.SerializerMethodField(
        read_only=True)

    class Meta:
        model = Follow
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribe', 'recipes', 'recipes_count'
        )

    def validate(self, data):
        user = self.context['request'].user
        author = get_object_or_404(User, id=data['id'])
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя')
        return super().validate(data)

    def get_is_subscribe(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return True

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        queryset = obj.author.recipes.all()
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return RecipeForSubscriptionSerializer(
            queryset, many=True, context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class RecipeForSubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    image = Base64ImageField(use_url=True, read_only=True)
    cooking_time = serializers.CharField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

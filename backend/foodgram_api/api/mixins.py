from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from .models import Recipe


class AddAndDeleteMixin:
    serializer_class = None
    model_class = None

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        recipe = get_object_or_404(
            Recipe, id=kwargs['recipe_id']
        )
        serializer.save(
            user=user,
            recipe=recipe
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        get_object_or_404(
            self.model_class,
            user=user,
            recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

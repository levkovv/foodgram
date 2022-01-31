# Generated by Django 4.0.1 on 2022-01-22 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', through='api.RecipeIngredient', to='api.Ingredient', verbose_name='Необходимые ингредиенты'),
        ),
    ]

# Generated by Django 3.2.3 on 2023-09-27 15:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_rename_name_recipe_recipes_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredients',
            name='id_ingredient',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='recipes.ingredients'),
        ),
        migrations.AlterField(
            model_name='recipeingredients',
            name='id_recipe',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='recipes.recipes'),
        ),
    ]
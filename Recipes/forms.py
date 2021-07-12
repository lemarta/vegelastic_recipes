from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm

from Recipes.models import Recipe, Ingredient

User = get_user_model()


class RecipeForm(ModelForm):

    class Meta:
        model = Recipe
        fields = ['name', 'meal_description', 'prep_time', 'prep_instructions', 'has_servings', 'servings']

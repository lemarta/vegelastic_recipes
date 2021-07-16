from Recipes.models import Recipe, Ingredient, RecipeCategory, User
from django.contrib.auth.models import Permission
from django.test import Client

import pytest


@pytest.fixture
def client():

    client = Client()
    return client

@pytest.fixture
def get_recipe():
    test_recipe = Recipe.objects.create(name='test recipe', has_servings=True, servings=1, prep_time=10)
    return test_recipe


@pytest.fixture
def get_ingredient():
    test_ingredient = Ingredient.objects.create(name='test ingredient')
    return test_ingredient


@pytest.fixture
def get_category():
    test_category = RecipeCategory.objects.create(name=1)
    return test_category


@pytest.fixture
def get_user():
    p = Permission.objects.get(codename='add_recipe')
    test_user = User.objects.create_user(username='RickSanchez', password='GrassTastesBad')
    test_user.user_permissions.add(p)
    return test_user
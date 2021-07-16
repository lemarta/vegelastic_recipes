from Recipes.models import Recipe, Ingredient, RecipeCategory, User

from django.contrib.auth.models import Permission
from django.test import Client

import pytest


@pytest.fixture
def client():
    """
    Configures a client for tests in a form of a dummy Web browser

    @return: the client
    """
    client = Client()
    return client

@pytest.fixture
def get_recipe():
    """
    Populates the database with a test recipe

    @return: the test recipe
    """
    test_recipe = Recipe.objects.create(name='test recipe', has_servings=True, servings=1, prep_time=10)
    return test_recipe


@pytest.fixture
def get_ingredient():
    """
    Populates the database with a test ingredient

    @return: the test ingredient
    """
    test_ingredient = Ingredient.objects.create(name='test ingredient')
    return test_ingredient


@pytest.fixture
def get_category():
    """
    Populates the database with a test category

    @return: the test category
    """
    test_category = RecipeCategory.objects.create(name=1)
    return test_category


@pytest.fixture
def get_user():
    """
    Populates the database with an user and gives it permission to add recipes to database

    @return: the user
    """
    p = Permission.objects.get(codename='add_recipe')
    test_user = User.objects.create_user(username='RickSanchez', password='GrassTastesBad')
    test_user.user_permissions.add(p)
    return test_user
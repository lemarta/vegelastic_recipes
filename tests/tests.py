import pytest

from Recipes.models import Recipe, Ingredient, RecipeCategory
from Recipes.views import CATEGORIES_PL


def test_index(client):
    """
    Checks that index page loads successfully

    @param client: from client pytest fixture
    """
    response = client.get('/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_login(client, get_user):
    """
    Checks that login page loads successfully and redirects when credentials are correct

    @param client: client from client pytest fixture
    @param get_user: test user from get_user pytest fixture
    """
    response = client.get('/login/')
    assert response.status_code == 200

    username = 'RickSanchez'
    password_success = 'GrassTastesBad'
    password_failure = 'WubbaLubbaDubDub'

    response_post_success = client.post('/login/', {
        'username': username,
        'password': password_success,

    })

    assert response_post_success.status_code == 302
    response_post_failure = client.post('/login/', {
        'username': username,
        'password': password_failure,

    })
    assert response_post_failure.status_code == 200


@pytest.mark.django_db
def test_logout(client, get_user):
    """
    Checks that logout page redirects successfully

    @param client: client from client pytest fixture
    """
    response = client.get('/logout/')
    assert response.status_code == 302


@pytest.mark.django_db
def test_recipe(get_recipe, client):
    """
    Checks that recipe page loads successfully

    @param get_recipe: test recipe from get_recipe pytest fixture
    @param client: client from client pytest fixture
    """
    test_recipe = Recipe.objects.get(name='test recipe')

    response_get = client.get(f'/przepis/{test_recipe.slug}/')
    assert response_get.status_code == 200
    assert response_get.context['recipe'] == test_recipe

    response_post = client.post(f'/przepis/{test_recipe.slug}/')
    assert response_post.status_code == 200
    assert response_post.context['recipe'] == test_recipe


@pytest.mark.django_db
def test_ingredient(get_ingredient, client):
    """
    Checks that ingredient page loads successfully

    @param get_ingredient: test ingredient from get_ingredient pytest fixture
    @param client: client from client pytest fixture
    """
    test_ingredient = Ingredient.objects.get(name='test ingredient')

    response = client.get(f'/skladnik/{test_ingredient.slug}/')
    assert response.status_code == 200
    assert response.context['ingredient'] == test_ingredient


def test_categories(client):
    """
    Checks that categories page loads successfully

    @param client: client from client pytest fixture
    """
    response = client.get('/kategorie/')
    assert response.status_code == 200
    assert response.context['categories'] == CATEGORIES_PL


@pytest.mark.django_db
def test_category(get_category, client):
    """
    Checks that category page loads successfully

    @param get_category: test category from get_category pytest fixture
    @param client: client from client pytest fixture
    """
    test_category = RecipeCategory.objects.get(name=1)

    response = client.get(f'/kategoria/{test_category.name}/')
    assert response.status_code == 200
    assert response.context['category_name'] == CATEGORIES_PL[1]


@pytest.mark.django_db
def test_add_recipe(client, get_user):
    """
    Checks that adding recipe page loads successfully and redirects after saving to database

    @param client: client from client pytest fixture
    @param get_user: test user from get_user pytest fixture
    """
    client.login(username='RickSanchez', password='GrassTastesBad')
    response_get = client.get('/dodaj/przepis/')
    assert get_user.has_perm("Recipes.add_recipe")
    assert response_get.status_code == 200
    assert response_get.context['message'] == 'Dodaj przepis'

    name = 'test recipe'
    has_servings = True
    servings = 1
    prep_time = 10
    response_post = client.post('/dodaj/przepis/', {
        'name': name,
        'has_servings': has_servings,
        'servings': servings,
        'prep_time': prep_time
    })
    assert response_post.status_code == 302


@pytest.mark.django_db
def test_searchbar(client):
    """
    Checks that search results page loads successfully and transfers searched value to the context

    @param client: client from client pytest fixture
    """
    response_get = client.get('/szukaj/')
    assert response_get.status_code == 200

    searched = 'placki'
    response_post = client.post('/szukaj/', {'searched': searched})
    assert response_post.status_code == 200
    assert response_post.context['searched'] == 'placki'

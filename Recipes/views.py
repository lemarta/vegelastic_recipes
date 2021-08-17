from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.views import View
from django.contrib.auth import get_user_model, login, authenticate, logout

from Recipes.models import Recipe, RecipeImage, RecipeIngredient, Ingredient, IngredientImage, RecipeCategory
from Recipes.forms import RecipeForm

# Create your views here.

User = get_user_model()

CATEGORIES_PL = {
    1: "śniadania",
    2: "kolacje",
    3: "obiady",
    4: "lunche",
    5: "desery",
    6: "inne",
}

TEASPOON_GRAMMAR_PL = {
    1: "łyżeczka",
    2: "łyżeczki",
    5: "łyżeczek",
    0: "łyżeczki",
}

TABLESPOON_GRAMMAR_PL = {
    1: "łyżka",
    2: "łyżki",
    5: "łyżek",
    0: "łyżki",
}

GLASS_GRAMMAR_PL = {
    1: "szklanka",
    2: "szklanki",
    5: "szklanek",
    0: "szklanki",
}

PINCH_GRAMMAR_PL = {
    1: "szczypta",
    2: "szczypty",
    5: "szczypt",
    0: "szczypty",
}

GRAM_GRAMMAR_PL = {
    1: "gram",
    2: "gramy",
    5: "gramów",
    0: "grama",
}

TO_TASTE_GRAMMAR_PL = {
    0: "do smaku",
}

UNIT_GRAMMAR_PL = {
    0, None,
}

PORTION_GRAMMAR_PL = {
    1: "porcję",
    2: "porcje",
    5: "porcji",
    0: "porcji",
}

MEASURE_GRAMMAR_PL = {
    1: TEASPOON_GRAMMAR_PL,
    2: TABLESPOON_GRAMMAR_PL,
    3: GLASS_GRAMMAR_PL,
    4: PINCH_GRAMMAR_PL,
    5: GRAM_GRAMMAR_PL,
    6: TO_TASTE_GRAMMAR_PL,
    7: UNIT_GRAMMAR_PL,
}

ACCEPTED_FRACTIONS = (0, 0.25, 0.33, 0.5, 0.67, 0.75)

FRACTIONS_DISPLAY = {
    0: "",
    0.25: "1/4",
    0.33: "1/3",
    0.5: "1/2",
    0.67: "2/3",
    0.75: "3/4",
}


class MainPageView(View):
    """
    Index page view
    # TODO: create main page here
    """
    def get(self, request, *args, **kwargs):
        """
        Generates the index page
        """
        context = {}
        return render(request=request, template_name='base.html', context=context)


class RecipeDetailsView(View):
    """
    Handles presentation of details of a specific recipe; allows for a user to recalculate the recipe to another
    amount of servings
    """

    def get(self, request, *args, **kwargs):
        """
        Finds recipe based on the slug, filters its details and first from of available pictures from database
        as well as all ingredients required to prepare this recipe and lists the data;
        sets multiplier in a cookie as 1
        """

        recipe_slug = kwargs['slug']
        recipe = Recipe.objects.get(slug=recipe_slug)
        recipe_ingredients = RecipeIngredient.objects.filter(recipe_id=recipe.pk)
        try:
            recipe_image = RecipeImage.objects.filter(recipe_id=recipe.pk)[0]
        except IndexError:
            recipe_image = None

        response = HttpResponse()

        servings_multiplier = 1

        response.set_cookie(key='servings_multiplier', value=servings_multiplier)

        portions_grammar_name, dynamic_portions = calculate_dynamic_portions(recipe, servings_multiplier)

        recipe_ingredients_data = get_recipe_ingredients_data(recipe_ingredients, servings_multiplier)

        context = {
            'recipe': recipe,
            'recipe_image': recipe_image,
            'portions_grammar_name': portions_grammar_name,
            'dynamic_portions': dynamic_portions,
            'recipe_ingredients_data': recipe_ingredients_data,
        }
        template = get_template('Recipes/recipe-details.html')
        response.write(template.render(context=context, request=request))

        return response

    def post(self, request, *args, **kwargs):
        """
        Finds recipe based on the slug, filters its details and first from of available pictures from database
        as well as all ingredients required to prepare this recipe and lists the data;
        overwrites the multiplier stored in a cookie and recalculates the portions and required ingredients based on it
        """

        recipe_slug = kwargs['slug']
        recipe = Recipe.objects.get(slug=recipe_slug)
        recipe_ingredients = RecipeIngredient.objects.filter(recipe_id=recipe.pk)

        try:
            recipe_image = RecipeImage.objects.filter(recipe_id=recipe.pk)[0]
        except IndexError:
            recipe_image = None

        response = HttpResponse()

        if request.COOKIES.get('servings_multiplier'):
            servings_multiplier = int(request.COOKIES.get('servings_multiplier'))
            servings_modifier = request.POST.get('modify_servings')
            if servings_modifier == 'more' and servings_multiplier < 5:
                servings_multiplier += 1
                response.set_cookie(key='servings_multiplier', value=servings_multiplier)
            elif servings_modifier == 'less' and servings_multiplier > 1:
                servings_multiplier -= 1
                response.set_cookie(key='servings_multiplier', value=servings_multiplier)
        else:
            servings_multiplier = 1

        portions_grammar_name, dynamic_portions = calculate_dynamic_portions(recipe, servings_multiplier)

        recipe_ingredients_data = get_recipe_ingredients_data(recipe_ingredients, servings_multiplier)

        context = {
            'recipe': recipe,
            'recipe_image': recipe_image,
            'portions_grammar_name': portions_grammar_name,
            'dynamic_portions': dynamic_portions,
            'recipe_ingredients_data': recipe_ingredients_data,
        }
        template = get_template('Recipes/recipe-details.html')
        response.write(template.render(context=context, request=request))

        return response


def calculate_dynamic_portions(recipe, servings_multiplier):
    """
    Recalculates the default amount of portions and applies grammar to name based on a servings multiplier stored in a
    cookie

    @param recipe: recipe for which portions are calculated
    @param servings_multiplier: currently selected amount of servings sourced from a cookie
    @return: amount of portions and grammatically correct name
    """
    dynamic_portions = recipe.servings * servings_multiplier
    if dynamic_portions == 1:
        portions_grammar_name = PORTION_GRAMMAR_PL[1]
    elif dynamic_portions in [2, 3, 4]:
        portions_grammar_name = PORTION_GRAMMAR_PL[2]
    elif dynamic_portions >= 5 and dynamic_portions % 1 == 0:
        portions_grammar_name = PORTION_GRAMMAR_PL[5]
    else:
        portions_grammar_name = PORTION_GRAMMAR_PL[0]
    return portions_grammar_name, dynamic_portions


def find_closest_value_in_list(lst, val):
    """
    From a list finds value that is arithmetically closest to a given value

    @param lst: list of accepted values
    @param val: value that will be checked against lst
    @return: closest matching value from lst
    """
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - val))]


def find_fraction_display(recipe_ingredient, servings_multiplier):
    if recipe_ingredient.measure in (4, 6):
        requires_amount_display = False
        has_decimal_place = False
        dynamic_amount_decimal_part_display = None
        fraction_display = None
    else:
        requires_amount_display = True
        dynamic_amount = recipe_ingredient.amount * servings_multiplier
        dynamic_amount_fractional_part = dynamic_amount % 1
        closest_accepted_fraction = find_closest_value_in_list(ACCEPTED_FRACTIONS, dynamic_amount_fractional_part)
        if closest_accepted_fraction != 0:
            fraction_display = FRACTIONS_DISPLAY[closest_accepted_fraction]
        else:
            fraction_display = None
        if dynamic_amount >= 1:
            has_decimal_place = True
            dynamic_amount_decimal_part = int(dynamic_amount - dynamic_amount_fractional_part)
            dynamic_amount_decimal_part_display = str(dynamic_amount_decimal_part)
        else:
            has_decimal_place = False
            dynamic_amount_decimal_part_display = None
    return requires_amount_display, has_decimal_place, dynamic_amount_decimal_part_display, fraction_display


def dynamic_grammar_name(recipe_ingredient, servings_multiplier):
    """
    Generates grammatically correct grammar name of ingredient and/or measure of an ingredient based on selected amount
    of servings

    @param recipe_ingredient: collection of data about and ingredient including mesure type, amount and several
    grammatical name options
    @param servings_multiplier: currently selected amount of servings sourced from a cookie
    @return: grammatically correct name of ingredient and/or measure for a given amount of it
    """
    measure = recipe_ingredient.measure
    dynamic_amount = recipe_ingredient.amount * servings_multiplier
    measure_pl_grammar_dict = MEASURE_GRAMMAR_PL[measure]
    requires_measure_name = True
    if measure == 7:
        requires_measure_name = False
        measure_name = None
        if dynamic_amount == 1:
            ingredient_name = recipe_ingredient.ingredient.name_one
        elif dynamic_amount in [2, 3, 4]:
            ingredient_name = recipe_ingredient.ingredient.name_two
        elif dynamic_amount >= 5 and dynamic_amount % 1 == 0:
            ingredient_name = recipe_ingredient.ingredient.name_five
        else:
            ingredient_name = recipe_ingredient.ingredient.name_half
    elif measure in (1, 2, 3, 5):
        if dynamic_amount == 1:
            measure_name = measure_pl_grammar_dict[1]
        elif dynamic_amount in [2, 3, 4]:
            measure_name = measure_pl_grammar_dict[2]
        elif dynamic_amount >= 5 and dynamic_amount % 1 == 0:
            measure_name = measure_pl_grammar_dict[5]
        else:
            measure_name = measure_pl_grammar_dict[0]
        ingredient_name = recipe_ingredient.ingredient.name_half
    elif measure == 4:
        measure_name = measure_pl_grammar_dict[1]
        ingredient_name = recipe_ingredient.ingredient.name_half
    elif measure == 6:
        measure_name = measure_pl_grammar_dict[0]
        ingredient_name = recipe_ingredient.ingredient.name_one
    return requires_measure_name, ingredient_name, measure_name


def get_recipe_ingredients_data(recipe_ingredients, servings_multiplier):
    """
    Dynamically recalculates the amount of ingredient required based on the currently selected amount of servings and
    applies correct grammar

    @param recipe_ingredients: collection of information about every ingredient required for a recipe for a
    default amount of servings
    @param servings_multiplier: currently selected amount of servings sourced from a cookie
    @return: collection of information about every ingredient required for a recipe appropriate for a current selection
    of servings
    """
    recipe_ingredients_data = []
    for recipe_ingredient in recipe_ingredients:
        requires_display, has_decimal_place, decimal, fraction = find_fraction_display(recipe_ingredient,
                                                                                       servings_multiplier)
        requires_measure_name, ingredient_name, measure_name = dynamic_grammar_name(recipe_ingredient,
                                                                                    servings_multiplier)
        recipe_ingredient_data = {
            'recipe_ingredient': recipe_ingredient,
            'requires_display': requires_display,
            'has_decimal_place': has_decimal_place,
            'decimal': decimal,
            'fraction': fraction,
            'requires_measure_name': requires_measure_name,
            'ingredient_name': ingredient_name,
            'measure_name': measure_name,
        }
        recipe_ingredients_data.append(recipe_ingredient_data)
    return recipe_ingredients_data


class IngredientDetailsView(View):
    """
    View showing details of an ingredient
    """
    def get(self, request, *args, **kwargs):
        """
        Finds ingredient based on the slug, filters its details and first from of available pictures from database
        as well as all recipes that include this ingredient and lists the data
        """
        ingredient_slug = kwargs['slug']
        ingredient = Ingredient.objects.get(slug=ingredient_slug)
        ingredient_recipes = RecipeIngredient.objects.filter(ingredient_id=ingredient.pk)
        try:
            ingredient_image = IngredientImage.objects.filter(ingredient_id=ingredient.pk)[0]
        except IndexError:
            ingredient_image = None

        context = {
            'ingredient': ingredient,
            'ingredient_image': ingredient_image,
            'ingredient_recipes': ingredient_recipes,
        }

        return render(request, template_name='Recipes/ingredient-details.html', context=context)


class RecipeCategoriesView(View):
    """
    View listing all categories
    """
    def get(self, request, *args, **kwargs):
        """
        Generates a view with listed categories
        """
        context = {
            'categories': CATEGORIES_PL
        }
        return render(request, template_name='Recipes/recipe-categories.html', context=context)


class RecipeCategoryView(View):
    """
    View listing all recipes in a selected category
    """
    def get(self, request, *args, **kwargs):
        """
        Finds category based on the primary key from the slug, filters all recipes classified in this category and
        renders a page listing them
        """
        category_key = kwargs['pk']
        category_name = CATEGORIES_PL[category_key]
        try:
            category_recipes = RecipeCategory.objects.filter(name=category_key)[0].recipe.all()
        except IndexError:
            category_recipes = []

        recipes_data = []

        for recipe in category_recipes:
            try:
                recipe_image = RecipeImage.objects.filter(recipe_id=recipe.pk)[0]
            except IndexError:
                recipe_image = None
            recipes_data.append({
                'recipe': recipe,
                'recipe_image': recipe_image,
            })

        context = {
            'category_name': category_name,
            'recipes_data': recipes_data,
        }

        return render(request, template_name='Recipes/category.html', context=context)


class AddRecipeView(LoginRequiredMixin, View):
    """
    View handling the process of saving a new recipe to the database
    """
    def get(self, request, *args, **kwargs):
        """
        Renders an empty form for a new recipe
        """
        form = RecipeForm()
        message = 'Dodaj przepis'

        context = {
            'form': form,
            'message': message,
        }

        return render(request, template_name='Recipes/add-recipe.html', context=context)

    def post(self, request, *args, **kwargs):
        """
        Intercepts new recipe data from a form and saves it to a database, then redirects to index page
        """
        form = RecipeForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            meal_description = form.cleaned_data['meal_description']
            prep_time = form.cleaned_data['prep_time']
            prep_instructions = form.cleaned_data['prep_instructions']
            has_servings = form.cleaned_data['has_servings']
            servings = form.cleaned_data['servings']

            recipe = Recipe.objects.create(
                name=name,
                meal_description=meal_description,
                prep_time=prep_time,
                prep_instructions=prep_instructions,
                has_servings=has_servings,
                servings=servings,
            )

            return redirect('/')

          
class SearchResultsView(View):
    """
    View handling the searching process
    """

    def get(self, request, *args, **kwargs):
        """
        Renders empty search result page
        """
        context = {}
        return render(request, template_name='Recipes/search-results.html', context=context)

    def post(self, request, *args, **kwargs):
        """
        Intercepts searched phrase and runs a check in the database against recipes and ingredients containing it in
        their names, then renders a view with a list of matching results
        """
        searched = request.POST.get('searched')
        recipes = Recipe.objects.filter(name__icontains=searched)
        ingredients = Ingredient.objects.filter(name__icontains=searched)
        search_results = []

        for recipe in recipes:
            try:
                recipe_image = RecipeImage.objects.filter(recipe_id=recipe.pk)[0]
            except IndexError:
                recipe_image = None
            search_results.append({
                'recipe': recipe,
                'recipe_image': recipe_image,
            })

        for ingredient in ingredients:
            if ingredient.is_searchable:
                try:
                    ingredient_image = IngredientImage.objects.filter(ingredient_id=ingredient.pk)[0]
                except IndexError:
                    ingredient_image = None
                search_results.append({
                    'ingredient': ingredient,
                    'ingredient_image': ingredient_image,
                })

        context = {
            'searched': searched,
            'search_results': search_results
        }

        return render(request, template_name='Recipes/search-results.html', context=context)


class UserLoginView(View):
    """
    View handling login process
    """
    def get(self, request, *args, **kwargs):
        """
        Renders login form
        """
        return render(request, 'login.html')

    def post(self, request, *args, **kwargs):
        """
        Either logs user in and redirects to index page if credentials are correct or renders again
        """
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, 'login.html')


class UserLogoutView(View):
    """
    View handling logout process
    """
    def get(self, request, *args, **kwargs):
        """
        Logs out currently logged in user and redirects to index page
        """
        logout(request)
        return redirect("index")
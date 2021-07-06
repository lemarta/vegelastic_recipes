from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views import View

from Recipes.models import Recipe, RecipeImage, RecipeIngredient

# Create your views here.

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
    1: "porcja",
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

    def get(self, request, *args, **kwargs):
        context = {}
        return render(request=request, template_name='base.html', context=context)


class RecipeDetailsView(View):

    def get(self, request, *args, **kwargs):

        recipe_slug = kwargs['slug']
        recipe = Recipe.objects.get(slug=recipe_slug)
        recipe_ingredients = RecipeIngredient.objects.filter(recipe_id=recipe.pk)
        recipe_image = RecipeImage.objects.filter(recipe_id=recipe.pk)[0]

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

        recipe_slug = kwargs['slug']
        recipe = Recipe.objects.get(slug=recipe_slug)
        recipe_ingredients = RecipeIngredient.objects.filter(recipe_id=recipe.pk)
        recipe_image = RecipeImage.objects.filter(recipe_id=recipe.pk)[0]

        response = HttpResponse()

        cookie = request.COOKIES.get('servings_multiplier')

        if cookie:
            print(cookie)
        else:
            print('empty')

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
    measure = recipe_ingredient.measure
    dynamic_amount = recipe_ingredient.amount * servings_multiplier
    measure_pl_grammar_dict = MEASURE_GRAMMAR_PL[measure]
    requires_measure_name = True
    if measure == 7:
        requires_measure_name = False
        measure_name = measure_pl_grammar_dict[0]
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

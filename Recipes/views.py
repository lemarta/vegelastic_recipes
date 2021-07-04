from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from Recipes.models import Recipe, RecipeImage, RecipeIngredient


# Create your views here.


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

        request.session['servings_multiplier'] = 1

        context = {
            'recipe': recipe,
            'recipe_image': recipe_image,
            'recipe_ingredients': recipe_ingredients,
        }

        return render(request=request, template_name='Recipes/recipe-details.html', context=context)

    def post(self, request, *args, **kwargs):

        recipe_slug = kwargs['slug']
        recipe = Recipe.objects.get(slug=recipe_slug)
        recipe_ingredients = RecipeIngredient.objects.filter(recipe_id=recipe.pk)
        recipe_image = RecipeImage.objects.filter(recipe_id=recipe.pk)[0]

        servings_multiplier = request.session.get('servings_multiplier')
        if servings_multiplier is None:
            return HttpResponse("Servings_multiplier doesn't exist in this session")

        servings_modifier = request.POST.get('modify_servings')
        if servings_modifier == 'more' and servings_multiplier < 10:
            request.session['servings_multiplier'] += 1
        elif servings_modifier == 'less' and servings_multiplier > 1:
            request.session['servings_multiplier'] -= 1

        context = {
            'recipe': recipe,
            'recipe_image': recipe_image,
            'recipe_ingredients': recipe_ingredients,
        }

        return render(request=request, template_name='Recipes/recipe-details.html', context=context)

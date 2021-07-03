from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
import Recipes.models as recipes_models


# Register your models here.
admin.site.register(recipes_models.User, UserAdmin)
# admin.site.register(recipes_models.Recipe)
admin.site.register(recipes_models.RecipeCategory)
admin.site.register(recipes_models.Ingredient)
admin.site.register(recipes_models.RecipeIngredient)
admin.site.register(recipes_models.RecipeImage)
admin.site.register(recipes_models.IngredientImage)


@admin.register(recipes_models.Recipe)
class RecipeModelAdmin(admin.ModelAdmin):
    fields = ['name', 'meal_description', 'prep_time', 'prep_instructions', 'has_servings', 'servings']
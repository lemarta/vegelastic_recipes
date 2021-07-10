from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.contrib.sessions.models import Session


# Create your models here.
CATEGORY_CHOICES = (
    (1, "breakfasts"),
    (2, "suppers"),
    (3, "dinners"),
    (4, "lunches"),
    (5, "desserts"),
    (6, "other"),
)

MEASURE_CHOICES = (
    (1, "teaspoon"),
    (2, "tablespoon"),
    (3, "glass"),
    (4, "pinch"),
    (5, "gram"),
    (6, "to taste"),
    (7, "unit")
)


def find_closest_value_in_list(lst, val):
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - val))]


class User(AbstractUser):
    pass


class Recipe(models.Model):
    name = models.CharField(max_length=256, unique=True)
    meal_description = models.TextField(blank=True)
    prep_time = models.PositiveSmallIntegerField(null=True, blank=True)
    prep_instructions = models.TextField(blank=True)
    has_servings = models.BooleanField()
    servings = models.PositiveSmallIntegerField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=256, blank=True)

    @property
    def prep_time_hours(self):
        prep_time = self.prep_time
        if prep_time >= 60:
            has_hours = True
            prep_time_hour_modulo = prep_time % 60
            hours = (prep_time - prep_time_hour_modulo) / 60
            if prep_time_hour_modulo != 0:
                minutes = prep_time_hour_modulo
            else:
                minutes = None
        else:
            has_hours = False
            hours = None
            minutes = prep_time
        result = {
            'has_hours': has_hours,
            'hours': hours,
            'minutes': minutes,
        }
        return result

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=256, unique=True)
    name_one = models.CharField(max_length=256)
    name_two = models.CharField(max_length=256)
    name_five = models.CharField(max_length=256)
    name_half = models.CharField(max_length=256)
    recipe = models.ManyToManyField(Recipe, through="RecipeIngredient")
    is_searchable = models.BooleanField(default=False)
    slug = models.SlugField(max_length=256, blank=True)
    ingredient_description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class RecipeCategory(models.Model):
    name = models.IntegerField(choices=CATEGORY_CHOICES)
    recipe = models.ManyToManyField(Recipe)

    def __str__(self):
        return self.get_name_display()



class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredients')
    measure = models.IntegerField(choices=MEASURE_CHOICES)
    amount = models.FloatField()

    def __str__(self):
        return f'Recipe: {self.recipe.name} ingredient: {self.ingredient.name}'


class RecipeImage(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_images')
    image = models.ImageField(upload_to='recipe/')

    def __str__(self):
        return f'{self.recipe.name} picture {self.pk}'


class IngredientImage(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredient_images')
    image = models.ImageField(upload_to='ingredient/')

    def __str__(self):
        return f'{self.ingredient.name} picture {self.pk}'

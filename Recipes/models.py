from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser

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


class User(AbstractUser):
    pass


class Recipe(models.Model):
    name = models.CharField(max_length=256, unique=True)
    meal_description = models.TextField(blank=True)
    prep_time = models.PositiveSmallIntegerField(null=True, blank=True)
    prep_instructions = models.TextField(blank=True)
    has_servings = models.BooleanField()
    servings = models.PositiveSmallIntegerField(null=True, blank=True)
    servings_multiplier = models.PositiveSmallIntegerField(default=1, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=256, blank=True)

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

    def __str__(self):
        return self.name


class RecipeCategory(models.Model):
    name = models.IntegerField(choices=CATEGORY_CHOICES)
    recipe = models.ManyToManyField(Recipe)

    def __str__(self):
        return self.get_name_display()


class RecipeIngredient(models.Model):
    ingredient_description = models.TextField(blank=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredients')
    measure = models.IntegerField(choices=MEASURE_CHOICES)
    amount = models.FloatField()

    def __str__(self):
        return f'Recipe: {self.recipe.name} ingredient: {self.ingredient.name}'

    @property
    def grammar_name(self):
        if (self.amount * self.recipe.servings_multiplier) == 1:
            return self.ingredient.name_one
        elif 2 <= (self.amount * self.recipe.servings_multiplier) <= 4:
            return self.ingredient.name_two
        elif (self.amount * self.recipe.servings_multiplier) >= 5:
            return self.ingredient.name_five
        elif (self.amount * self.recipe.servings_multiplier) <= 1:
            return self.ingredient.name_half
        else:
            return self.ingredient.name


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

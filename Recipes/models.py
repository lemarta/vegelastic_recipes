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


class User(AbstractUser):
    """
    Overrides default User model
    """
    pass


class Recipe(models.Model):
    """
    Creates a model of a recipe
    """
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
        """
        Transforms recipe preparation time from minutes to hours and minutes if applicable
        @return: has_hours: flags if time is at least an hour; hours: full hours; minutes: reminder of minutes
        """
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
        """
        Overrides save method for slug field to populate it with string derived from name field
        """
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Populates string representation of object of class Recipe with value from it's name field

        @return: name field value
        """
        return self.name


class Ingredient(models.Model):
    """
    Creates a model of an ingredient that can be linked with recipes through RecipeIngredient class
    """
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
        """
        Overrides save method for slug field to populate it with string derived from name field
        """
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Populates string representation of object of class Ingredient with value from it's name field

        @return: name field value
        """
        return self.name


class RecipeCategory(models.Model):
    """
    Creates a model that allows to sort recipes in different categories
    """
    name = models.IntegerField(choices=CATEGORY_CHOICES)
    recipe = models.ManyToManyField(Recipe)

    def __str__(self):
        """
        Populates string representation of object of class RecipeCategory with value from it's name field

        @return: name field value
        """
        return self.get_name_display()


class RecipeIngredient(models.Model):
    """
    Creates a model that allows to link different recipes and ingredients
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredients')
    measure = models.IntegerField(choices=MEASURE_CHOICES)
    amount = models.FloatField()

    def __str__(self):
        """
        Populates string representation of object of class RecipeIngredient with value from name fields of related
        recipe and ingredient

        @return: Recipe: recipe name field value, ingredient: ingredient name field value
        """
        return f'Recipe: {self.recipe.name} ingredient: {self.ingredient.name}'


class RecipeImage(models.Model):
    """
    Creates a model of picture related to a recipe
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_images')
    image = models.ImageField(upload_to='recipe/')

    def __str__(self):
        """
        Populates string representation of object of class RecipeImage with value from name field of
        recipe and primary key number of a picture related to it

        @return: Recipe name field value, picture: picture primary key number
        """
        return f'{self.recipe.name} picture {self.pk}'


class IngredientImage(models.Model):
    """
    Creates a model of picture related to an ingredient
    """
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredient_images')
    image = models.ImageField(upload_to='ingredient/')

    def __str__(self):
        """
        Populates string representation of object of class IngredientImage with value from name field of
        ingredient and primary key number of a picture related to it

        @return: Ingredient name field value, picture: picture primary key number
        """
        return f'{self.ingredient.name} picture {self.pk}'

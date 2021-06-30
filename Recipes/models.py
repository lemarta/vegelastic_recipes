from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser

# Create your models here.
CATEGORY_CHOICES = (
    (1, "śniadania"),
    (2, "kolacje"),
    (3, "obiady"),
    (4, "lunche"),
    (5, "desery"),
    (6, "inne"),
)

MEASURE_CHOICES = (
    (1, "łyżka"),
    (2, "łyżeczka"),
    (3, "szklanka"),
    (4, "szczypta"),
    (5, "gram"),
    (6, "do smaku"),
    (7, "sztuka")
)


class User(AbstractUser):
    pass


class Recipe(models.Model):
    name = models.CharField(max_length=256, unique=True)
    meal_description = models.TextField(max_length=2048, null=True, blank=True)
    prep_time = models.PositiveSmallIntegerField(null=True, blank=True)
    prep_instructions = models.TextField(max_length=2048, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=256)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Recipe, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=256, unique=True)
    name_one = models.CharField(max_length=256)
    name_two = models.CharField(max_length=256)
    name_five = models.CharField(max_length=256)
    name_half = models.CharField(max_length=256)
    recipe = models.ManyToManyField(Recipe, through="RecipeIngredient")

    def __str__(self):
        return self.name


class RecipeCategory(models.Model):
    name = models.IntegerField(choices=CATEGORY_CHOICES)
    recipe = models.ManyToManyField(Recipe)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    ingredient_description = models.TextField(max_length=1024, null=True, blank=True)
    is_searchable = models.BooleanField(default=False)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredient')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredient')
    measure = models.IntegerField(choices=MEASURE_CHOICES)
    amount = models.FloatField()

    @property
    def grammar_name(self):
        if self.amount == 1:
            return self.ingredient.name_one
        elif 2 <= self.amount <= 4:
            return self.ingredient.name_two
        elif self.amount >= 5:
            return self.ingredient.name_five
        elif self.amount <= 1:
            return self.ingredient.name_half
        else:
            return self.ingredient.name


class RecipeImage(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_image')
    image = models.ImageField(upload_to='media/')


class IngredientImage(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredient_image')
    image = models.ImageField(upload_to=f'media/')

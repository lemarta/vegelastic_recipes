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


def find_closest_value_in_list(lst, val):
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - val))]


def get_servings_multiplier():
    sessions = Session.objects.all()
    decoded_session = sessions[1].get_decoded()
    servings_multiplier = decoded_session['servings_multiplier']
    return servings_multiplier


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

    @property
    def dynamic_portions(self):

        servings_multiplier = get_servings_multiplier()
        dynamic_portions = self.servings * servings_multiplier
        if dynamic_portions == 1:
            portions_grammar_name = PORTION_GRAMMAR_PL[1]
        elif dynamic_portions in [2, 3, 4]:
            portions_grammar_name = PORTION_GRAMMAR_PL[2]
        elif dynamic_portions >= 5 and dynamic_portions % 1 == 0:
            portions_grammar_name = PORTION_GRAMMAR_PL[5]
        else:
            portions_grammar_name = PORTION_GRAMMAR_PL[0]
        result = {
            'portions_grammar_name': portions_grammar_name,
            'dynamic_portions': dynamic_portions,
        }
        return result

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
    def find_fraction_display(self):
        servings_multiplier = get_servings_multiplier()
        if self.measure in (4, 6):
            requires_amount_display = False
            has_decimal_place = False
            dynamic_amount_decimal_part_display = None
            fraction_display = None
        else:
            requires_amount_display = True
            dynamic_amount = self.amount * servings_multiplier
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
        result = {
            'needs_display': requires_amount_display,
            'has_decimal_place': has_decimal_place,
            'decimal': dynamic_amount_decimal_part_display,
            'fraction': fraction_display,
        }
        return result

    @property
    def dynamic_grammar_name(self):
        servings_multiplier = get_servings_multiplier()
        measure = self.measure
        dynamic_amount = self.amount * servings_multiplier
        measure_pl_grammar_dict = MEASURE_GRAMMAR_PL[measure]
        requires_measure_name = True
        if measure == 7:
            requires_measure_name = False
            measure_name = measure_pl_grammar_dict[0]
            if dynamic_amount == 1:
                ingredient_name = self.ingredient.name_one
            elif dynamic_amount in [2, 3, 4]:
                ingredient_name = self.ingredient.name_two
            elif dynamic_amount >= 5 and dynamic_amount % 1 == 0:
                ingredient_name = self.ingredient.name_five
            else:
                ingredient_name = self.ingredient.name_half
        elif measure in (1, 2, 3, 5):
            if dynamic_amount == 1:
                measure_name = measure_pl_grammar_dict[1]
            elif dynamic_amount in [2, 3, 4]:
                measure_name = measure_pl_grammar_dict[2]
            elif dynamic_amount >= 5 and dynamic_amount % 1 == 0:
                measure_name = measure_pl_grammar_dict[5]
            else:
                measure_name = measure_pl_grammar_dict[0]
            ingredient_name = self.ingredient.name_half
        elif measure == 4:
            measure_name = measure_pl_grammar_dict[1]
            ingredient_name = self.ingredient.name_half
        elif measure == 6:
            measure_name = measure_pl_grammar_dict[0]
            ingredient_name = self.ingredient.name_one
        result = {
            'requires_measure_name': requires_measure_name,
            'ingredient_name': ingredient_name,
            'measure_name': measure_name,
        }
        return result


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

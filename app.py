from get_recipes import build_recipes_from_ingredients
from read_recipes_from_file import read_recipe_to_markdown
from apikey import get_apikey

def generate_recipes(ingredients, num_recipes):
    apikey = get_apikey()
    f = build_recipes_from_ingredients(apikey, ingredients, num_recipes)
    md = read_recipe_to_markdown(f)
    print(f'Recipes saved to {md}')
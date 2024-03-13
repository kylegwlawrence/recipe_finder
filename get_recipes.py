# api endpoints
import requests
import json
import time
from read_recipes_from_file import read_recipe

def get_recipes_by_ingredients(apikey, ingredients:str, num_recipes_returned:int, ranking):
    """api limit of 150 per day and 1 call per second. Each call uses 1 point and each recipes returned is 0.01 point"""
    # format ingredients string for url
    ingredients = ingredients.replace(',',',+')
    if ranking == 'max_used_ingredients':
        rank = 1
    elif ranking == 'min_missing_ingredients':
        rank = 2
    url = f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&number={num_recipes_returned}&ranking={rank}&apiKey={apikey}'
    r = requests.get(url)
    recipes_contents = r.text
    time.sleep(1.5)
    return recipes_contents

def get_recipe_instructions(apikey, recipe_id:int):
    # format ingredients string for url
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions?apiKey={apikey}'
    r = requests.get(url)
    instructions_contents = r.text
    time.sleep(1.5)
    return instructions_contents

def parse_instructions(instructions_content) -> list[str]:
    """Generate readable instructions by parsing instructions response"""
    recipe_instructions = []
    data = json.loads(instructions_content)
    for entry in data:
        # keep keys equipment, number, step in


        for instruction_step in entry.get('steps'):
            string = f"Step {instruction_step.get('number')}: {instruction_step.get('step')}"
            equipment = []
            for tool in instruction_step.get('equipment')[0]:
                equipment.append({instruction_step.get('number'):tool})
            
            recipe_instructions.append(string)
    return recipe_instructions

def parse_recipes(recipes_contents) -> list[dict]:
    """return list of tuples with id and recipe name"""
    recipes = []
    data = json.loads(recipes_contents)
    for recipe in data:
        d = {}
        d['id'] = recipe.get('id')
        d['name'] = recipe.get('title')
        used_ingredients = []
        missed_ingredients = []
        unused_ingredients = []
        for ingredient in recipe.get('usedIngredients'):
            used_ingredients.append(ingredient.get('original'))
        for ingredient in recipe.get('missedIngredients'):
            missed_ingredients.append(ingredient.get('original'))
        for ingredient in recipe.get('unusedIngredients'):
            unused_ingredients.append(ingredient.get('original'))
        d['used_ingredients'] = used_ingredients
        d['missed_ingredients'] = missed_ingredients
        d['unused_ingredients'] = unused_ingredients
        recipes.append(d)
    return recipes

def build_recipes_from_ingredients(apikey, ingredients:str, num_recipes:int) -> list[dict]:
    """Take a a number of ingredients as csv list and saves a file and returns the saved filename"""
    recipes_contents = get_recipes_by_ingredients(apikey, ingredients, num_recipes)
    recipes = parse_recipes(recipes_contents)
    for recipe in recipes:
        recipe_id = recipe.get('id')
        instructions_contents = get_recipe_instructions(apikey, recipe_id)
        recipe_instructions = parse_instructions(instructions_contents)
        recipe['instructions'] = recipe_instructions
    # write recipes to file
    timestr = time.strftime("%Y%m%d-%H%M%S")
    ingredients = ingredients.replace(', ','-').replace(' ','')
    file_name = f'recipes/{ingredients}_{num_recipes}_{timestr}.txt'
    with open(file_name, 'w') as f:
        json.dump(recipes, f)
    return file_name

if __name__ == '__main__':
    apikey = 'a5e1c05d6d4442ad88338e361aafc1f6'
    ingredients = 'cauliflower, cheese, onion, broccoli'
    num_recipes = 5

    f = build_recipes_from_ingredients(apikey, ingredients, num_recipes)
    read_recipe(f)
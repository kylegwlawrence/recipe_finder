# api endpoints
import requests
import json
import time
from read_recipes_from_file import read_recipe

def get_recipes_by_ingredients(apikey, ingredients:str, num_recipes_returned:int, use_sample='no'):
    """api limit of 150 per day and 1 call per second. Each call uses 1 point and each recipes returned is 0.01 point"""
    if use_sample.lower()=='yes':
        with open('sample.txt') as f:
            recipes_contents = f.readlines()
    elif use_sample.lower()=='no':
        apikey = 'a5e1c05d6d4442ad88338e361aafc1f6'
        # format ingredients string for url
        ingredients = ingredients.replace(',',',+')
        url = f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&number={num_recipes_returned}&apiKey={apikey}'
        r = requests.get(url)
        recipes_contents = r.text
        time.sleep(1.5)
    return recipes_contents

def get_recipe_instructions(apikey, recipe_id:int, use_sample='no'):
    if use_sample.lower()=='yes':
        with open('sample_instructions.txt') as f:
            instructions_contents = f.readlines()
    elif use_sample.lower()=='no':
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
        for instruction_step in entry.get('steps'):
            string = f"Step {instruction_step.get('number')}: {instruction_step.get('step')}"
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

def build_recipes_from_ingredients(apikey, ingredients:str, num_recipes_returned:int, use_sample='yes') -> list[dict]:
    """Take a a number of ingredients as csv list and returns num_recipes_returned with instructions"""
    recipes_contents = get_recipes_by_ingredients(apikey, ingredients, num_recipes_returned, use_sample)
    recipes = parse_recipes(recipes_contents)
    for recipe in recipes:
        recipe_id = recipe.get('id')
        instructions_contents = get_recipe_instructions(apikey, recipe_id, use_sample)
        recipe_instructions = parse_instructions(instructions_contents)
        recipe['instructions'] = recipe_instructions
    # write recipes to file
    timestr = time.strftime("%Y%m%d-%H%M%S")
    ingredients = ingredients.replace(', ','-').replace(' ','')
    file_name = f'recipes/{ingredients}_{num_recipes_returned}_{timestr}.txt'
    with open(file_name, 'w') as f:
        json.dump(recipes, f)
    print(f'Recipes saved to {file_name}')
    return file_name

if __name__ == '__main__':
    apikey = 'a5e1c05d6d4442ad88338e361aafc1f6'
    ingredients = 'cauliflower, cheese, onion, broccoli'
    num_recipes_returned = 5
    use_sample = 'no'

    f = build_recipes_from_ingredients(apikey, ingredients, num_recipes_returned, use_sample)
    read_recipe(f)
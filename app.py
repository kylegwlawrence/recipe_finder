# api endpoints
import requests
import json
import time

def get_recipes_by_ingredients(apikey, ingredients:str, num_recipes_returned:int, use_sample='no'):
    """api limit of 150 per day and 1 call per second. Each call uses 1 point and each recipes returned is 0.01 point"""

    if use_sample.lower()=='yes':
        with open('sample.txt') as f:
            recipes_contents = f.readlines()
        #print(contents)

    elif use_sample.lower()=='no':
        apikey = 'a5e1c05d6d4442ad88338e361aafc1f6'

        # format ingredients string for url
        ingredients = ingredients.replace(',',',+')
        url = f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&number={num_recipes_returned}&apiKey={apikey}'

        r = requests.get(url)
        recipes_contents = r.text

    return recipes_contents

def get_recipe_instructions(apikey, recipe_id:int, use_sample='no'):

    if use_sample.lower()=='yes':
        with open('sample_instructions.txt') as f:
            instructions_contents = f.readlines()
        #print(contents)
    elif use_sample.lower()=='no':
        # format ingredients string for url
        url = f'https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions?apiKey={apikey}'
        r = requests.get(url)
        instructions_contents = r.text

    return instructions_contents

def instructions(instructions_contents) -> list[str]:
    """Generate readable instructions by parsing instructions response"""
    recipe_instructions = []
    for entry in instructions_contents:
        data = json.loads(entry)
        for instruction_step in data[0].get('steps'):
            string = f"Step {instruction_step.get('number')}: {instruction_step.get('step')}"
            recipe_instructions.append(string)
    return recipe_instructions

def recipe_names(recipes_contents) -> list[dict]:
    """return list of tuples with id and recipe name"""
    recipes = []
    for entry in recipes_contents:
        data = json.loads(entry)
        for recipe in data:
            d = {}
            d['id'] = recipe.get('id')
            d['name'] = recipe.get('title')
            recipes.append(d)
    return recipes

def build_recipes_from_ingredients(apikey, ingredients:str, num_recipes_returned:int, use_sample='yes') -> list[dict]:
    """Take a a number of ingredients as csv list and returns num_recipes_returned with instructions"""
    recipes_contents = get_recipes_by_ingredients(apikey, ingredients, num_recipes_returned, use_sample)
    recipes = recipe_names(recipes_contents)
    for recipe in recipes:
        recipe_id = recipe.get('id')
        instructions_contents = get_recipe_instructions(apikey, recipe_id, use_sample)
        recipe_instructions = instructions(instructions_contents)
        recipe['instructions'] = recipe_instructions

    return recipes

if __name__ == '__main__':
    apikey = 'a5e1c05d6d4442ad88338e361aafc1f6'
    ingredients = 'lamb, potato, olive oil'
    num_recipes_returned = 3
    recipes = build_recipes_from_ingredients(apikey, ingredients, num_recipes_returned, use_sample='yes')
    
    # write recipes to file
    timestr = time.strftime("%Y%m%d-%H%M%S")
    ingredients = ingredients.replace(', ','-').replace(' ','')
    with open(f'recipes/{ingredients}_{num_recipes_returned}_{timestr}.txt', 'w') as f:
        json.dump(recipes, f)






    #used_ingredients = data.get('usedIngredients')
    #unused_ingredients = data.get('unusedIngredients')
    #missed_ingredients = data.get('missedIngredients')

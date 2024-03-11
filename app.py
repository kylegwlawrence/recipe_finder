# api endpoints
import requests
import ast
import json

def get_recipes_by_ingredients(apikey, ingredients:str, num_recipes_returned:int, use_sample='no'):
    """api limit of 150 per day and 1 call per second. Each call uses 1 point and each recipes returned is 0.01 point"""

    if use_sample.lower()=='yes':
        with open('sample.txt') as f:
            response_contents = f.readlines()
        #print(contents)

    elif use_sample.lower()=='no':
        apikey = 'a5e1c05d6d4442ad88338e361aafc1f6'

        # format ingredients string for url
        ingredients = ingredients.replace(',',',+')
        url = f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&number={num_recipes_returned}&apiKey={apikey}'

        r = requests.get(url)
        response_contents = r.text

    return response_contents

def get_recipe_instructions(apikey, recipe_id:int, use_sample='no'):

    if use_sample.lower()=='yes':
        with open('sample_instructions.txt') as f:
            response_contents = f.readlines()
        #print(contents)
    elif use_sample.lower()=='no':
        # format ingredients string for url
        url = f'https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions?apiKey={apikey}'
        r = requests.get(url)
        response_contents = r.text

    return response_contents


def recipe_names(response_contents) -> list[tuple]:
    """return list of tuples with id and recipe name"""
    recipes = []
    for entry in response_contents:
        data = json.loads(entry)
        for recipe in data:
            recipe_name = recipe.get('title')
            recipe_id = recipe.get('id')
            recipes.append((recipe_id, recipe_name))
    return recipes

if __name__ == '__main__':
    apikey = 'a5e1c05d6d4442ad88338e361aafc1f6'
    response_contents = get_recipes_by_ingredients(apikey, use_sample = 'yes', ingredients = 'lamb, potato, olive oil', num_recipes_returned=3)
    
    recipes = recipe_names(response_contents)

    for recipe in recipes[0:1]:
        id = recipe[0]
        instructions_contents = get_recipe_instructions(apikey, recipe_id=id, use_sample='yes')
        print(instructions_contents)





    #used_ingredients = data.get('usedIngredients')
    #unused_ingredients = data.get('unusedIngredients')
    #missed_ingredients = data.get('missedIngredients')

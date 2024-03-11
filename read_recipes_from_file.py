import json

def read_recipe(recipe_file):
    """takes a saved recipe file, reads it, and produces a formatted readable recipe"""
    with open(recipe_file) as f:
        recipes = json.loads(f.readlines()[0])
    for r in recipes:
        print(r.get('name'))
        print('\nIngredients')
        for ingredient in r.get('used_ingredients'):
            print(f"- {ingredient}")
        for ingredient in r.get('missed_ingredients'):
            print(f"- {ingredient}")
        if len(r.get('unused_ingredients'))>0:
            print('\nUnused ingredients')
            for ingredient in r.get('unused_ingredients'):
                print(f"- {ingredient}")
        print('\nInstructions')
        for instruction in r.get('instructions'):
            print(f"- {instruction}")
        print("\n ------END OF RECIPE------ \n")

if __name__ == '__main__':
    f = 'recipes/beef-onions-celery-carrots-saffron-milk-kimchi_5_20240311-090134.txt'
    read_recipe(f)
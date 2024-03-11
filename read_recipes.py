import json

recipe_file = 'recipes/potato-bamboo-coconut-tofu_5_20240310-225654.txt'

with open(recipe_file) as f:
    recipes = json.loads(f.readlines()[0])

for r in recipes:
    print(r.get('name'))
    print('\n')
    print('Ingredients')
    for ingredient in r.get('ingredients'):
        print(f"- {ingredient}")
    print('\n')
    print('Instructions')
    for instruction in r.get('instructions'):
        print(f"- {instruction}")
    print("\n ------END OF RECIPE------ \n")


    
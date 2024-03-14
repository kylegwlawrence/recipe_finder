import json
from mdutils.mdutils import MdUtils

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

def read_recipe_to_markdown(recipe_file):
    """takes a recipe file, reads it, and returns a markdown formatted recipe"""
    with open(recipe_file) as f:
        recipes = json.loads(f.readlines()[0])
    print(type(recipes[0]))

    md_file_name = recipe_file.replace('.txt','').replace('recipes/','')
    ingredients = md_file_name.split('_')[0].replace('-',', ')
    md_file_name_full = f'md_recipes/recipes_{md_file_name}'

    mdFile = MdUtils(file_name = md_file_name_full, title = f'Recipes for {ingredients}')

    mdFile.new_header(level=3, title=f'Recipes:', add_table_of_contents='n')
    for r in recipes:
        r_name = r.get('name')
        mdFile.new_line(f'  - {r_name}')

    for r in recipes:
        r_name = r.get('name')
        # ingredients
        mdFile.new_header(level=2, title=f'{r_name}', add_table_of_contents='n')
        mdFile.new_header(level=3, title=f'Ingredients', add_table_of_contents='n')
        mdFile.new_header(level=4, title=f'Used ingredients', add_table_of_contents='n')
        for ingredient in r.get('used_ingredients'):
            mdFile.new_line(f'  - {ingredient}')
        mdFile.new_header(level=4, title=f'Missed ingredients', add_table_of_contents='n')
        for ingredient in r.get('missed_ingredients'):
            mdFile.new_line(f'  - {ingredient}')
        if len(r.get('unused_ingredients'))>0:
            mdFile.new_header(level=4, title=f'Unused ingredients', add_table_of_contents='n')
            for ingredient in r.get('unused_ingredients'):
                mdFile.new_line(f'  - {ingredient}')
        # instructions
        mdFile.new_header(level=3, title=f'Directions', add_table_of_contents='n')
        for instruction in r.get('instructions'):
            mdFile.new_line(f'  - {instruction}')
    mdFile.create_md_file()
    return f'{md_file_name_full}.md'

if __name__ == '__main__':
    f = 'recipes/beef-onions-celery-carrots-saffron-milk-kimchi_5_20240311-090134.txt'
    #read_recipe(f)
    md_file_name_full = read_recipe_to_markdown(f)
    print(md_file_name_full)
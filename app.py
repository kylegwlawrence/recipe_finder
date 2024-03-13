from apikey import get_apikey
from get_recipes import build_recipes_from_ingredients
from read_recipes_from_file import read_recipe_to_markdown
from recipe_to_github import recipe_to_github
from send_to_slack import send_to_slack

def generate_recipes(ingredients, num_recipes):
    apikey = get_apikey()
    f = build_recipes_from_ingredients(apikey, ingredients, num_recipes)
    md = read_recipe_to_markdown(f)
    github_link = recipe_to_github(md)
    send_to_slack(github_link)

if __name__ == '__main__':
    params = {'ingredients':'rice, tuna, tomato'
              , 'num_recipes':10
              }
    generate_recipes(**params)
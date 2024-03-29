import time
from my_classes import SearchRecipesByIngredients, RecipesInfoBulk, Recipe, ManyRecipesMarkdown, GithubPublisher, SlackMessageManyRecipes
import argparse

def app(args) -> None:
    search_ingredients = args.ingredients
    num_recipes = args.num_recipes

    # search for ingredients, get recipe ids, pass to Bulk recipe info, pass to Recipe, pass to manyMarkdown recipes
    file_name = f'md_recipes/{search_ingredients}_{time.strftime("%Y%m%d-%H%M%S")}.md'
    recipes_by_ingredients = SearchRecipesByIngredients(ingredients=search_ingredients, num_recipes=num_recipes)
    recipes_by_ingredients.get_recipes()
    recipes_ids = recipes_by_ingredients.get_recipe_ids()
    bulk_info = RecipesInfoBulk(recipes_ids).get_info()
    recipe_list = []
    for recipe_info in bulk_info:
        r = Recipe()
        r.info = recipe_info
        r.get_ingredients_from_info()
        r.get_instructions_from_info()
        r.get_equipment_from_instructions()
        r.get_name()
        r.get_servings()
        r.get_time()
        recipe_list.append(r)
    md = ManyRecipesMarkdown(recipe_list, file_name, searched_ingredients=search_ingredients)
    md.to_markdown()
    github = GithubPublisher(file_name)
    github_link = github.publish()
    channel_id = 'C06NZKA1L03'
    message = SlackMessageManyRecipes(channel_id, num_recipes, search_ingredients, github_link)
    message.send()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send recipe suggestion for these ingredients to a slack channel')
    parser.add_argument('--num_recipes', required=True, help='number of recipes to retrieve')
    parser.add_argument('--ingredients', required=True, help='a string of comma separated ingredients')
    args = parser.parse_args()

    app(args)
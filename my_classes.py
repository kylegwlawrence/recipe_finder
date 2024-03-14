import requests
import json
from mdutils.mdutils import MdUtils
import os
import git
import time
import urllib.request

def endpoint_base() -> str:
    return 'https://api.spoonacular.com'

def apikey() -> str:
    return 'a5e1c05d6d4442ad88338e361aafc1f6'

class Recipe:
    def __init__(self, recipe_id:str=None):
        self.apikey = apikey()

        self.recipe_id = recipe_id
        self.url_base = f'{endpoint_base()}/recipes/{self.recipe_id}'
        self.info = None
        self.instructions = None
    
    def get_info_from_api(self, includeNutrition:bool=True) -> dict:
        """
        Use a recipe id to get full information about a recipe, such as ingredients, nutrition, diet and allergen information, etc.
        """
        str_include_nutrition = str(includeNutrition).lower()
        url = f'{self.url_base}/information?includeNutrition={str_include_nutrition}&apiKey={self.apikey}'
        response = requests.get(url)
        self.info = json.loads(response.text)
        return self.info
    
    def get_ingredients_from_info(self):
        """
        Extract the ingredients from self.info
        """
        self.ingredients = None
    
    def get_instructions_from_info(self) -> list[dict]:
        """Extract the instructions from self.info
        :return: list of dicts
        """
        if self.info==None:
            raise AttributeError('No information exists. Please create info using Recipe.get_info() or pass in self.info')
        # parse out the instructions
        if not self.info.get('analyzedInstructions'):
            instructions = self.info.get('instructions')
            # create same list of dicts structure as analyzedInstructions key-value
            self.instructions = [{'step':instructions}]
        else:
            self.instructions = self.info.get('analyzedInstructions')[0].get('steps') # returns a list of dicts
        return self.instructions
        
    # get instructions from the information endpoint - there are two keys: instructions (raw string) and analyzedInstructions
    def get_instructions_from_api(self):
        url = f'{self.url_base}/analyzedInstructions?apiKey={self.apikey}'
        response = requests.get(url)
        self.instructions = json.loads(response.text)[0]
        return self.instructions
    
    def get_equipment_from_instructions(self) -> list[dict]:
        """
        Use result from get_instructions() to store equipment info in a list of
        """
        if self.instructions == None:
            raise AttributeError('No instructions exists. Please create info using Recipe.get_info() or pass in self.info')
        self.list_equipment = []
        for instruction in self.instructions:
            equipment = instruction.get('equipment')[0]
            self.list_equipment.append(equipment)
        return self.list_equipment
        
    def get_name(self) -> str:
        self.name = self.info.get('title')
        return self.name
    
    def get_servings(self) -> int:
        self.servings = self.info.get('servings')
        return self.servings
    
    def get_time(self):
        self.time = self.info.get('readyInMinutes')

    def get_taste_from_api(self) -> dict:
        url = f'{self.url_base}/tasteWidget.json?apiKey={self.apikey}'
        response = requests.get(url)
        self.taste = json.loads(response.text)
        print(self.taste)
        print(type(self.taste))
        return self.taste
    
    def to_markdown(self):
        """
        Either write formatting logic here or create a MarkdownRecipe class to format then save here.
        Simplest to format here since only applying to one class of object
        """
        self.recipe_in_markdown = RecipeMarkdown(self.ingredients, self.instructions, self.list_equipment, self.name, self.servings, self.time)
        
    
class RecipesInfoBulk:
    """
    Loop over the results of this using the Recipe class to generate attributes
    This endpoint costs 1 point for the first recipe and 0.5 points per additional recipe.
    """
    apikey = apikey()
    def __init__(self, recipe_ids:str) -> None:
        """
        :recipe_ids: a comma-separated string of recipe ids
        """
        self.recipe_ids = recipe_ids
        self.url = f'{endpoint_base()}/recipes/informationBulk?ids={self.recipe_ids}&includeNutrition=true&apiKey={self.apikey}'
    
    def get_info(self) -> list[dict]:
        response = requests.get(self.url)
        self.bulk_info = json.loads(response.text)
        return self.bulk_info

class SearchRecipesByIngredients:
    """
    Retrieve just the ids and ingredients from this and use the RecipesInfoBulk class to generate Recipe classes for each recipe_id.
    This endpoint returns the usage status of each ingredient that was passed plus the rest of the ingredients the recipe calls for.
    Although this endpoint comes with equipment, instructions have to be called separately per id.
    Instead pull all recipe info at once contained within same api response to obtain
    """
    apikey = apikey()
    def __init__(self, ingredients:str, num_recipes:int, rank_ingredients:str='maximize_used') -> None:
        self.ingredients = ingredients
        url_ingredients = ingredients.replace(', ',',+')
        self.num_recipes = num_recipes
        self.recipes = None
        self.file_name = f'recipes/{url_ingredients}_{self.num_recipes}_{time.strftime("%Y%m%d-%H%M%S")}.md'
        if rank_ingredients not in ['maximize_used', 'minimize_missing']:
            raise ValueError("Rank arg only accepts the string values 'maximize_used' and 'minimize_missing'")
        else:
            if rank_ingredients == 'maximize_used':
                self.rank = 1
            else:
                self.rank = 2
        self.url = f'{endpoint_base()}/recipes/findByIngredients?apiKey={self.apikey}&ingredients={self.ingredients}&number={self.num_recipes}&ranking={self.rank}'
    
    def get_recipes(self) -> list[dict]:
        response = requests.get(self.url)
        self.recipes = json.loads(response.text)
        return self.recipes
    
    def get_recipe_ids(self) -> list:
        self.recipe_ids = []
        for recipe in self.recipes:
            self.recipe_ids.append(recipe.get('id'))
        return self.recipe_ids
    
    def get_all_ingredients(self) -> list[dict]:
        """extract ingredients from the get_recipes()"""
        if self.recipes == None:
            raise AttributeError('No recipes exist. Please create recipes using get_recipes()')
        self.all_ingredients = []
        for recipe in self.recipes:
            dict_ingredients = {'recipe_id':recipe.get('id')}
            for ingredient_type in ['usedIngredients', 'missedIngredients', 'unusedIngredient']:
                dict_ingredients[ingredient_type] = recipe.get(ingredient_type)
            self.all_ingredients.append(dict_ingredients)
        return self.all_ingredients

class RecipeMarkdown:
    # make a class to build a recipe which would use either one recipe or RecipesByIngredients
    def to_markdown(self, recipe_info):
        if self.data==None:
            self.get_recipes()
        title = f'Recipes for {self.ingredients}'
        mdFile = MdUtils(self.file_name, title)
        # list the recipes at the top of the document
        mdFile.new_header(level=3, title=title, add_table_of_contents='n')
        for r in self.data:
            r_name = r.get('name')
            mdFile.new_line(f'  - {r_name}')
        # add one section for each recipe
        for r in self.data:
            r_name = r.get('name')
            # ingredients
            mdFile.new_header(level=2, title=f'{r_name}', add_table_of_contents='n')
            mdFile.new_header(level=3, title=f'Ingredients', add_table_of_contents='n')
            mdFile.new_header(level=4, title=f'Used ingredients', add_table_of_contents='n')
            for ingredient in r.get('usedIngredients'):
                mdFile.new_line(f"  - {ingredient.get('name')}")
            mdFile.new_header(level=4, title=f'Missed ingredients', add_table_of_contents='n')
            for ingredient in r.get('missedIngredients'):
                mdFile.new_line(f"  - {ingredient.get('name')}")
            if len(r.get('unusedIngredients'))>0:
                mdFile.new_header(level=4, title=f'Unused ingredients', add_table_of_contents='n')
                for ingredient in r.get('unused_ingredients'):
                    mdFile.new_line(f"  - {ingredient.get('name')}")
            # instructions
            mdFile.new_header(level=3, title=f'Directions', add_table_of_contents='n')
            for instruction in r.get('instructions'):
                mdFile.new_line(f'  - {instruction}')
        try:
            mdFile.create_md_file()
        except:
            print(f'Something went wrong saving {self.file_name} locally')

    def save_markdown(self):
        """
        Save the file separately from creating it
        """
        pass
        
    def publish_to_github(self, local_repo:str='/Users/kylelawrence/Documents/recipe_finder', open_browser:bool=False):
        """Pushes the markdown file to github from a local repo"""
        if not os.path.isfile(self.file_name):
            self.to_markdown()
        # define the local repo
        local_repo = git.Repo(local_repo)
        # add the changes
        local_repo.index.add([self.file_name]) 
        print('Files Added Successfully') 
        local_repo.index.commit(f'Save {self.file_name} to github') 
        print('Commited successfully')
        origin = local_repo.remote(name='origin')
        origin.push()
        print('Pushed changes to origin')
        self.github_link = f'https://github.com/kylegwlawrence/recipe_finder/blob/main/{self.file_name}'
        if open_browser:
            urllib.request.urlopen(self.github_link)
    
if __name__ == '__main__':
    search = SearchRecipesByIngredients('chicken, lemon', 2)
    search.get_recipes()
    list_ids = search.get_recipe_ids()
    string_ids = ', '.join(str(i) for i in map(str, list_ids))
    bulk = RecipesInfoBulk(string_ids)
    r_infos = bulk.get_info()
    all_recipes = []
    for recipe_info in r_infos:
        id = recipe_info.get('id')
        single_recipe = Recipe(id)
        single_recipe.info = recipe_info
        all_recipes.append(single_recipe) # list of Recipe objects


if __name__ == '__main':
    r = Recipe(recipe_id = 715438)
    info = r.get_info()
    instructions = r.get_instructions_from_info()
    #equipment = r.get_equipment_from_instructions()
    print(info)
    print(type(info))
    
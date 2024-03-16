import requests
import json
from mdutils.mdutils import MdUtils
import git
import time
import urllib.request
import spoonacular_api as spa
import logging
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def endpoint_base() -> str:
    return 'https://api.spoonacular.com'

def api_key() -> str:
    api_key = os.environ.get("SPOON_API_TOKEN")
    return api_key

class Recipe:
    def __init__(self, recipe_id:str=None):
        """
        :param recipe_id: the spoonacular recipe id as a string
        """
        self.api_key = api_key()
        root_endpoint = endpoint_base()

        self.recipe_id = recipe_id
        self.url_base = f'{root_endpoint}/recipes/{self.recipe_id}'
        self.info = None
        self.instructions = None
    
    def get_info_from_api(self, includeNutrition:bool=True) -> dict:
        """
        Use a recipe id to get full information about a recipe, 
        such as ingredients, nutrition, diet and allergen information, etc.
        """
        str_include_nutrition = str(includeNutrition).lower()
        url = f'{self.url_base}/information?includeNutrition={str_include_nutrition}&apiKey={self.api_key}'
        response = requests.get(url)
        self.info = json.loads(response.text)
        return self.info
    
    def get_ingredients_from_info(self) -> list:
        """
        Extract the ingredients from self.info
        """
        self.ingredients = []
        for ingredient in self.info.get('extendedIngredients'):
            original = ingredient.get('original')
            self.ingredients.append(original)
        return self.ingredients
    
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
        """
        Get the recipe instructions from the api endpoint analyzedInstructions
        """
        url = f'{self.url_base}/analyzedInstructions?apiKey={self.api_key}'
        response = requests.get(url)
        self.instructions = json.loads(response.text)[0]
        return self.instructions
    
    def get_equipment_from_instructions(self) -> list:
        """
        Use result from get_instructions() to store equipment info in a list.
        Optionally store the step number associated with the equipment.
        """
        if self.instructions == None:
            raise AttributeError('No instructions exists. Please create info using Recipe.get_info() or pass in self.info')
        self.list_tools = []
        for instruction in self.instructions:
            equipment = instruction.get('equipment')
            if equipment!=None:
                for tool in equipment:
                    tool_name = tool.get('name')
                    self.list_tools.append(tool_name)
        return self.list_tools
        
    def get_name(self) -> str:
        self.name = self.info.get('title')
        return self.name
    
    def get_servings(self) -> int:
        self.servings = self.info.get('servings')
        return self.servings
    
    def get_time(self) -> int:
        self.time = self.info.get('readyInMinutes')
        return self.time

    def get_taste_from_api(self) -> dict:
        url = f'{self.url_base}/tasteWidget.json?apiKey={self.api_key}'
        response = requests.get(url)
        self.taste = json.loads(response.text)
        print(self.taste)
        print(type(self.taste))
        return self.taste
    
class RecipesInfoBulk:
    """
    Loop over the results of this using the Recipe class to generate attributes
    This endpoint costs 1 point for the first recipe and 0.5 points per additional recipe.
    """
    api_key = api_key()
    def __init__(self, recipe_ids:str) -> None:
        """
        :param recipe_ids: a comma-separated string of recipe ids
        """
        self.recipe_ids = recipe_ids
        self.url = f'{endpoint_base()}/recipes/informationBulk?ids={self.recipe_ids}&includeNutrition=true&apiKey={self.api_key}'
    
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
        token = os.environ.get("SPOON_API_TOKEN")
        self.url = f'{endpoint_base()}/recipes/findByIngredients?apiKey={token}&ingredients={self.ingredients}&number={self.num_recipes}&ranking={self.rank}'
        print(f'---  {self.url}  ---')
    
    # need to handle failure responses like this: {'status': 'failure', 'code': 401, 'message': 'You are not authorized. Please read https://spoonacular.com/food-api/docs#Authentication'}
    def get_recipes(self) -> list[dict]:
        response = requests.get(self.url)
        self.recipes = json.loads(response.text)
        return self.recipes
    
    def get_recipe_ids(self) -> list:
        self.recipe_ids = []
        for recipe in self.recipes:
            self.recipe_ids.append(recipe.get('id'))
        return self.recipe_ids
    
    def get_categorized_ingredients(self) -> list[dict]:
        """extract ingredients from the get_recipes() method"""
        if self.recipes == None:
            raise AttributeError('No recipes exist. Please create recipes using get_recipes()')
        self.cat_ingredients = []
        for recipe in self.recipes:
            dict_ingredients = {'recipe_id':recipe.get('id')}
            for ingredient_cat in ['usedIngredients', 'missedIngredients', 'unusedIngredient']:
                dict_ingredients[ingredient_cat] = recipe.get(ingredient_cat)
            self.cat_ingredients.append(dict_ingredients)
        return self.cat_ingredients

class RecipeMarkdown:
    def __init__(self, name:str, servings:int, time:int, ingredients:list, instructions, equipment:list, file_name:str) -> None:
        """
        File name must include realtive path if not in root
        """
        self.name = name
        self.servings = servings
        self.time = time
        self.ingredients = ingredients
        self.instructions = instructions
        self.equipment = equipment
        self.file_name = file_name

    def to_markdown(self):
        """
        Write one recipe to a markdown file.
        """
        mdFile = MdUtils(self.file_name, self.name)

        # prep time and num servings
        mdFile.new_line(f"Ready in {self.time} mins | Servings: {self.servings}")

        # list ingredients
        mdFile.new_header(level=3, title=f'Ingredients', add_table_of_contents='n')
        for ingredient in self.ingredients:
            mdFile.new_line(f"  - {ingredient}")

        # list equipment
        mdFile.new_header(level=3, title=f'Equipment', add_table_of_contents='n')
        for tool in self.equipment:
            mdFile.new_line(f"  - {tool}")

        # list instructions
        mdFile.new_header(level=3, title=f'Instructions', add_table_of_contents='n')
        for instruction in self.instructions:
            mdFile.new_line(f"  - Step {instruction.get('number')}: {instruction.get('step')}\n")

        # save locally
        try:
            mdFile.create_md_file()
        except:
            print(f'Something went wrong saving {self.file_name} locally')

class ManyRecipesMarkdown:
    def __init__(self, recipe_markdown_instances:list, file_name:str, searched_ingredients:str) -> None:
        """
        takes in a list of RecipeMarkdown instances and combines them into one file.
        useful for creating a file of recipes that are found through SearchRecipesByIngredients
        """
        self.markdown_recipes = recipe_markdown_instances
        self.file_name = file_name
        self.searched_ingredients = searched_ingredients

    def to_markdown(self): 
        """
        itereate over the list of RecipeMarkdown objects and create one markdown file
        """
        title = f'Recipes for {self.searched_ingredients}'
        mdFile = MdUtils(file_name=self.file_name, title=title)

        # list the recipes at the top of the document
        for md_recipe in self.markdown_recipes:
            mdFile.new_line(f'  - {md_recipe.name}')

        # add one section for each recipe
        for md_recipe in self.markdown_recipes:
            mdFile.new_header(level=2, title=md_recipe.name, add_table_of_contents='n')
            # prep time and num servings
            mdFile.new_line(f"Ready in {md_recipe.time} mins | Servings: {md_recipe.servings}")

            # list ingredients
            mdFile.new_header(level=3, title=f'Ingredients', add_table_of_contents='n')
            for ingredient in md_recipe.ingredients:
                mdFile.new_line(f"  - {ingredient}")

            # list equipment
            mdFile.new_header(level=3, title=f'Equipment', add_table_of_contents='n')
            for tool in md_recipe.list_tools:
                mdFile.new_line(f"  - {tool}")

            # list instructions
            mdFile.new_header(level=3, title=f'Instructions', add_table_of_contents='n')
            for instruction in md_recipe.instructions:
                mdFile.new_line(f"  - Step {instruction.get('number')}: {instruction.get('step')}\n")
        try:
            mdFile.create_md_file()
        except:
            print(f'Something went wrong saving {self.file_name} locally')
        
class GithubPublisher:
    def __init__(self, file_name, repo = None) -> None:
        self.file_name = file_name
        if repo==None:
            self.repo = git.Repo('/Users/kylelawrence/Documents/recipe_finder')
        else:
            self.repo = repo 

    def publish(self, open_browser:bool=False):
        """Pushes the markdown file to github from a local repo"""
        # add the changes
        self.repo.index.add([self.file_name]) 
        print('Files Added Successfully') 
        self.repo.index.commit(f'Save {self.file_name} to github') 
        print('Commited successfully')
        origin = self.repo.remote(name='origin')
        origin.push()
        print('Pushed changes to origin')
        self.github_link = f'https://github.com/kylegwlawrence/recipe_finder/blob/main/{self.file_name}'
        if open_browser:
            urllib.request.urlopen(self.github_link)
        return self.github_link

class SlackMessageManyRecipes:
    def __init__(self, channel_id, num_recipes, search_ingredients, github_link) -> None:
        self.channel_id = channel_id
        self.num_recipes = num_recipes
        self.search_ingredients = search_ingredients
        self.github_link = github_link

    def send(self) -> None:
        """Send a message with a link to slack"""
        logger = logging.getLogger(__name__)

        # contruct the message string
        msg=f"{self.num_recipes} new recipes for {self.search_ingredients} in <{self.github_link}|Github>"

        # instantiate the webclient with a bot token
        try:
            client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
        except SlackApiError as e:
            logger.error("Error creating client: {}".format(e))
        
        # send the message
        try:
            # call app.client.chat_postMessage
            result = client.chat_postMessage(
                channel=self.channel_id,
                text=msg
            )
            logger.info(result)
        except SlackApiError as e:
            logger.error("Error uploading file: {}".format(e))
            # send failure message to slack channel
            try:
                result = client.chat_postMessage(
                    channel=self.channel_id,
                    text="File upload to Slack failed."
                )
                logger.info(result)
            except SlackApiError as e:
                logger.error("Error sending failure message: {}".format(e))   

if __name__ == '__main__':
    # search for ingredients, get recipe ids, pass to Bulk recipe info, pass to Recipe, pass to manyMarkdown recipes
    search_ingredients = 'chicken, cabbage'
    file_name = f'md_recipes/{search_ingredients}_{time.strftime("%Y%m%d-%H%M%S")}.md'
    num_recipes = 5
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
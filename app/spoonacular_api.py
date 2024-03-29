import requests
import json
import os
import time

class ApiClient:
    # what does an api client do?
    def __init__(self) -> None:
        # retrieve the api token from environment variables
        self.api_key=os.environ.get("SPOON_API_TOKEN")
        # creates a root url
        self.root_endpoint = 'https://api.spoonacular.com'

    def wait(self, seconds=1.5):
        """
        Wait for some seconds until the next call can be made
        """
        time.sleep(seconds)
        print(f'Waiting {seconds} to make next api call')

    def make_request(self, url):
        self.url = url
        response = requests.get(self.url)
        self.response_json = json.loads(response.text)
        return self.response_json

    def post_request(self, url, api_key):
        print('Use example from this stackoverflow response: https://stackoverflow.com/questions/65265786/python-call-rest-api-to-get-data-from-url')
        session = requests.Session()
        credentials = {"apiKey": api_key}
        headers = {"accept": "application/json", 
                "content-type": "application/json"
                }
        response = session.post(url, headers=headers, json=credentials, verify=False)
        self.session_id = response.json()["sessionID"]
        return self.session_id
    
    def get_request(self, url, session_id):
        url = "https://hpe.sysnergy.com/rest/resource-alerts"
        headers = {"accept": "application/json", 
                "content-type": "application/json", 
                "auth": session_id, 
                }
        session = requests.Session()
        response = session.get(url, headers=headers, verify=False)
        return response
    
class ApiEndpoint:
    def __init__(self) -> None:
        self.api_client = ApiClient()
        self.api_key = self.api_client.api_key
        self.root_endpoint = self.api_client.root_endpoint

    def recipe_information(self, recipe_id, include_nutrition:bool=True):
        """
        Use a recipe id to get full information about a recipe, 
        such as ingredients, nutrition, diet and allergen information, etc.
        """
        self.include_nutrition = str(include_nutrition).lower()
        self.url = f'{self.root_endpoint}/recipes/{recipe_id}/information?includeNutrition={include_nutrition}&apiKey={self.api_key}'
        self.info = self.api_client.make_request(self.url)
        self.api_client.wait()
        return self.info

if __name__ == '__main__':
    endpoint = ApiEndpoint()
    info = endpoint.recipe_information(recipe_id=645704)
    print(info)
    #print(api.post_request(url = '', api_key=api.api_key))
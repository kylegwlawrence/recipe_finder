import requests
import json
import os


class ApiClient:
    # what does an api client do?
    def __init__(self) -> None:
        # retrieve the api token from environment variables
        self.api_key=os.environ.get("SPOON_API_TOKEN")
        # creates a root url
        self.root_endpoint = 'https://api.spoonacular.com'
    
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
        pass

    def recipe_information(self, recipe_id, include_nutrition:bool=True):
        """
        Use a recipe id to get full information about a recipe, 
        such as ingredients, nutrition, diet and allergen information, etc.
        """
        #instantiate api client
        api_client = ApiClient()
        include_nutrition = str(include_nutrition).lower()
        # construct the url
        url = f'{api_client.root_endpoint}/information?includeNutrition={include_nutrition}'
        
        # make post request
        session_id = api_client.post_request(url=url, api_key=api_client.api_key)
        # make get request using session id
        response = api_client.get_request(url, session_id)
        self.info = json.loads(response.text)
        return self.info

if __name__ == '__main__':
    api = ApiClient()
    print(api.post_request(url = '', api_key=api.api_key))
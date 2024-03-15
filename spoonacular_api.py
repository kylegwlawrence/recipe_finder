import requests
import json
import os


class ApiClient:
    # what does an api client do?
    def __init__(self) -> None:
        # retrieve the api token
        self.api_key=os.environ.get("SPOON_API_TOKEN")
        # creates a root url
        self.root_endpoint = 'https://api.spoonacular.com'
    
    def post_request(self, url, api_key):
        print('Use example from this stackoverflow response: https://stackoverflow.com/questions/65265786/python-call-rest-api-to-get-data-from-url')
        session = requests.Session()
        url = "https://hpe.sysnergy.com/rest/login-sessions"
        credentials = {"apiKey": api_key}
        headers = {"accept": "application/json", 
                "content-type": "application/json", 
                "x-api-version": "120", 
                }
        response = session.post(url, headers=headers, json=credentials, verify=False)

        self.session_id = response.json()["sessionID"]
        return self.session_id
    
    def get_request(self, url, session_id):
        url = "https://hpe.sysnergy.com/rest/resource-alerts"
        headers = {"accept": "application/json", 
                "content-type": "text/csv", 
                "x-api-version": "2", 
                "auth": session_id, 
                }
        session = requests.Session()
        response = session.get(url, headers=headers, verify=False)
        return response
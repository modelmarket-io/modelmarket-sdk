import json
import requests
import pandas as pd


class Client:
    def __init__(self, server_url="https://api.modelmarket.io", debug=False):
        self.server_url = server_url
        self.access_token = ""
        self.refresh_token = ""
        self.debug = debug

    def authenticate(self, username, password):
        url = self.server_url + "/oauth/token"

        if self.debug:
            print("Auth url: ", url)

        payload = json.dumps({
            "username": username,
            "password": password
        })

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=payload)

        # Check HTTP status code
        if response.status_code != 200:
            raise Exception(f"Failed to authenticate: {response.status_code} {response.reason}")

        try:
            # Try to parse the JSON response
            json_response = response.json()
        except ValueError:
            raise Exception("Failed to parse JSON response")

        # Check if 'access_token' and 'refresh_token' are in the JSON response
        if 'access_token' not in json_response or 'refresh_token' not in json_response:
            raise Exception("Missing expected keys in JSON response")

        self.access_token = json_response['access_token']
        self.refresh_token = json_response['refresh_token']

    def models(self, input_features={}, provider="", model_name="", model_type="normal", raise_exception_on_fail=True):
        url = self.server_url + "/v1/models/" + model_type + "/" + provider + "/" + model_name
        # print(url)
        headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.access_token
            }

        payload = json.dumps(input_features)
    
        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 401:
            raise Exception(
                f"Response:{response.text}")

        if raise_exception_on_fail:
            if response.status_code != 200:
                raise Exception(
                    f"Response:{response.json()}" )
    
        return response.json()

    def df_api_input(self, df):
        payload = df.to_json(orient="split")
        parsed_payload = json.loads(payload)

        # Extract the 'data' field and convert it to a Dict to match your desired format
        payload_dict = {}
        for index, column_name in enumerate(parsed_payload['columns']):
            payload_dict[column_name] = [row[index] for row in parsed_payload['data']]

        return payload_dict

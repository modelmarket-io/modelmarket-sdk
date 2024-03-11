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
            'Content-Type': 'application/x-www-form-urlencoded'
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

    def models(self, df, provider="", model_name="", model_type="normal", chunk_size=10000):
        url = self.server_url + "/v1/models/" + model_type + "/" + provider + "/" + model_name
        # print(url)
        predict_column = provider + "-" + model_name
        full_predictions_df = pd.DataFrame()

        # Iterate through DataFrame chunks
        for i in range(0, len(df), chunk_size):
            chunk_df = df.iloc[i:i + chunk_size]

            # Extract the 'data' field and convert it to a Dict to match your desired format
            payload_dict = self.df_api_input(df)
            # print(self.access_token)
            payload = json.dumps(payload_dict)
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.access_token
            }

            # Make the request
            response = requests.post(url, headers=headers, data=payload)

            # Check if the request was successful
            if response.status_code != 200:
                raise Exception(
                    f"You do not have the necessary permissions to access this model. Please check your access rights or contact the administrator for assistance. Error:[{response.status_code}]")

                # Extract the predictions
            predictions = response.json()['predictions']
            # print(predictions)
            predictions_df = pd.DataFrame(list(predictions.items()), columns=['row_nr',
                                                                              predict_column])

            # Concatenate the prediction chunks
            full_predictions_df = pd.concat([full_predictions_df, predictions_df], ignore_index=True)

        return full_predictions_df[predict_column]

    def df_api_input(self, df):
        payload = df.to_json(orient="split")
        parsed_payload = json.loads(payload)

        # Extract the 'data' field and convert it to a Dict to match your desired format
        payload_dict = {}
        for index, column_name in enumerate(parsed_payload['columns']):
            payload_dict[column_name] = [row[index] for row in parsed_payload['data']]

        return payload_dict

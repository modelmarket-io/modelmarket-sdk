import json
import requests
import pandas as pd


class Client:
    def __init__(self, server_url="http://api.modelmarket.io"):
        self.server_url = server_url
        self.access_token = ""
        self.refresh_token = ""

    def authenticate(self, username, password):
        url = self.server_url + "/oauth/token"

        payload = json.dumps({
            "username": username,
            "password": password
        })

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        json_response = response.json()
        self.access_token = json_response['access_token']
        # print(self.acces_token)
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

    def df_api_input(df):
        payload = df.to_json(orient="split")
        parsed_payload = json.loads(payload)

        # Extract the 'data' field and convert it to a Dict to match your desired format
        payload_dict = {}
        for index, column_name in enumerate(parsed_payload['columns']):
            payload_dict[column_name] = [row[index] for row in parsed_payload['data']]

        return payload_dict

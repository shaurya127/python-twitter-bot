import csv
import requests
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Twitter API credentials
bearer_token = os.getenv("BEARER_TOKEN")
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

# Set the API endpoint URL
url = "https://api.twitter.com/2/users/1661016790548492292/following"

# Read the CSV file and extract the username
with open("list.csv", newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        username = row["handle"].replace("@", "")  # Remove '@' from the username

        # Set the target user ID of the account you want to follow
        target_user_id = None

        # Construct the API request URL to fetch the user ID
        user_lookup_url = f"https://api.twitter.com/2/users/by/username/{username}"
        headers = {
            "Authorization": f"Bearer {bearer_token}"
        }

        # Send the GET request to fetch the user ID
        response = requests.get(user_lookup_url, headers=headers)

        # Check the response status code
        if response.status_code == 200:
            user_data = response.json()
            if "data" in user_data:
                target_user_id = user_data["data"]["id"]
            else:
                print(f"User ID not found in the response for username: {username}")
                continue
        else:
            print(f"Failed to fetch user ID for username: {username}. Status code: {response.status_code}, Message: {response.text}")
            continue

        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )
        # Set the request body
        data = {
            "target_user_id": target_user_id
        }

        # Send the POST request to follow the user
        response = oauth.post(url, json=data)
    
        # Check the response status code
        if response.status_code == 200:
            print(f"Successfully followed the user with ID: {target_user_id}")
        else:
            print(f"Error following the user with ID: {target_user_id}. Status code: {response.status_code}, Message: {response.text}")

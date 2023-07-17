import csv
import requests
import openai
from dotenv import load_dotenv
import os
from telegram import Bot
import asyncio
import tweepy
import schedule
import time

load_dotenv()

# Set up Twitter API credentials
bearer_token = os.getenv("BEARER_TOKEN")
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

# Set up OpenAI API credentials
openai.api_key = os.getenv("OPENAI_API_KEY")

bot_token = '6062435791:AAHhm3SSh-u9ygq-YWwYg14WBd2lnrc02Fg'
group_ids = ['-845538975', '-844376939']  # Add more group IDs here

# Initialize the Telegram bot
bot = Bot(token=bot_token)

# CSV file paths
csv_file = "tweet.csv"
reply_csv_file = "reply.csv"

# Process each Twitter link from the CSV file
async def process_twitter_links():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    with open(csv_file, newline="") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row if it exists

        for row in reader:
            if len(row) >= 1:
                twitter_link = row[0]

                # Extract the tweet_id from the Twitter link
                tweet_id = twitter_link.split("/")[-1]

                # Construct the API request URL
                url = f"https://api.twitter.com/2/tweets/{tweet_id}?tweet.fields=author_id,text"

                # Set the authorization header with the bearer token
                headers = {
                    "Authorization": f"Bearer {bearer_token}"
                }

                # Send the API request
                response = requests.get(url, headers=headers)

                # Check if the request was successful
                if response.status_code == 200:
                    tweet_data = response.json()
                    tweet_text = tweet_data["data"]["text"]
                    author_id = tweet_data["data"]["author_id"]
                    # Process the tweet details as needed
                    print(f"The user {author_id} tweeted: '{tweet_text}'")

                    # Prompt options for different personality styles
                    personalities = {
                        "supportive": "You're doing great! Keep it up.",
                        "snarky": "Wow, what a brilliant tweet... not!",
                        "optimistic": "The future is looking bright with tweets like these.",
                        "controversial": "Your tweet has sparked a heated debate!",
                        "excited": "This tweet has got me jumping with joy!",
                        "humorous": "Haha, that's a tweet I won't forget!"
                    }

                    # Select the desired personality style
                    selected_personality = "excited"  # Change this to the desired style

                    prompt = f"The user @{author_id} tweeted: '{tweet_text}'\n"
                    prompt += personalities.get(selected_personality, "")

                    response = openai.Completion.create(
                        engine="text-davinci-003",
                        prompt=prompt,
                        max_tokens=50,  # Adjust the number of tokens to control the response length
                        n=1,
                        stop=None,
                        temperature=0.7
                    )

                    reply = response.choices[0].text.strip()

                    print("Generated reply:", reply)
                    if reply:
                        # for group_id in group_ids:

                        #     await bot.send_message(chat_id=group_id, text=twitter_link)  # Send the tweet link first
                        #     await asyncio.sleep(1)  # Add a delay between messages
                        #     await bot.send_message(chat_id=group_id, text=reply)  # Send the reply text

                        with open("reply.csv", "a", newline="") as reply_file:
                            writer = csv.writer(reply_file)
                            writer.writerow([reply, twitter_link, 0])  # Add the reply text, tweet link, and flag (0)
                            print("Reply saved to file: reply.csv")
                    else:
                        print("Generated reply is empty, skipping sending the message")
                else:
                    print("Failed to retrieve tweet details. Error:", response.status_code)

def job():
    asyncio.run(process_twitter_links())

# Schedule the job to run every hour
schedule.every(30).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

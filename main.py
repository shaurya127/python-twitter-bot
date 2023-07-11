import requests
from requests_oauthlib import OAuth1Session
import csv
import time
import os
from telegram import Bot
import asyncio


# Twitter API credentials
bearer_token = "AAAAAAAAAAAAAAAAAAAAAK0EogEAAAAA9n4cKvHvkKRKf%2BDdBKyYPLIZWEA%3Duuv8jnrPt1UaY7EFnAwd32up8wEbLwnPIU1PwAA1qqdLetyNUF"
consumer_key = "UU4G0YZ5u2Efg494N08l00rHL"
consumer_secret = "3yvG30sYpJbPdA9RXKtJ4Tt8O564y6ij6Wx6jHieSuYxvBntHW"
access_token ="1661016790548492292-KhgxTQWjmH2ys33gH59JcoAZ4FIQrW"
access_token_secret = "E68iOZAkwraQKBVpLKKaxmKVvv0J1AR5YZ6rO0oCuJTwt"

bot_token = '6062435791:AAHhm3SSh-u9ygq-YWwYg14WBd2lnrc02Fg'
group_ids = ['-845538975', '-844376939']  # Add more group IDs here

# Initialize the Telegram bot
bot = Bot(token=bot_token)

def create_tweet(tweet_text, tweet_link, access_token, access_token_secret):
    url = "https://api.twitter.com/2/tweets"
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )
    payload = {"text": f"{tweet_text}\n\n{tweet_link}"}
    response = oauth.post(url, json=payload)

    if response.status_code != 201:
        raise Exception("Request returned an error: {} {}".format(response.status_code, response.text))

    tweet_id = response.json()["data"]["id"]
    return tweet_id


async def process_reply_csv():
    reply_csv_file = "reply.csv"
    tweet_text = ""
    tweet_link = ""
    row_index = -1

    with open(reply_csv_file, newline="") as file:
        reader = csv.reader(file)
        rows = list(reader)
        for i, row in enumerate(rows):
            if len(row) >= 3 and int(row[2]) == 0:
                tweet_link = row[1]
                tweet_text = row[0]
                row_index = i
                break

    if tweet_text and tweet_link:
        tweet_id = create_tweet(tweet_text, tweet_link, access_token, access_token_secret)
        print("Tweet posted successfully. Tweet ID:", tweet_id)

        for group_id in group_ids:
            await bot.send_message(chat_id=group_id, text=tweet_link)  # Send the tweet link first
            await asyncio.sleep(1)  # Add a delay between messages
            await bot.send_message(chat_id=group_id, text=tweet_text)  # Send the reply text

        if row_index >= 0:
            rows[row_index][2] = "1"
            with open(reply_csv_file, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(rows)
            print("Flag updated to 1 in reply.csv for row index:", row_index)
    else:
        print("No unused text found in reply.csv")


async def job():
    await process_reply_csv()


async def run_scheduler():
    while True:
        await job()
        await asyncio.sleep(30)  # Delay between job executions


# Run the scheduler using asyncio
asyncio.run(run_scheduler())

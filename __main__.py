#WHEN THIS RUNS, (SHOULD RUN AS DICTATED BY CRON JOB) IT SHOULD
#1. READ REFRESH TOKEN FROM ENVIRONMENT (SET BY temp_auth.server.py)
#2. USE REFRESH TOKEN TO GENERATE NEW ACCESS/REFRESH TOKEN
#3. UPDATE ENV VARIABLE WITH NEW REFRESH TOKEN
#4. INITIALIZE TWEEPY SESSION WITH CLIENT(ACCESS TOKEN)

#NOTE: Save yourself some debugging in the future. This method of generating refresh token will not work unless
#your type of app in Twitter Dev is set under the Public Client category

#TODO -- Implement job scheduling to run this script.
#TODO -- Inheritance for twitter module
#TODO -- build twitter module
#TODO -- build mlb api client, initialize it here

import os
import redis
import json
import requests
from requests.auth import AuthBase, HTTPBasicAuth
from requests_oauthlib import OAuth2Session, TokenUpdated
import tweepy
import statsapi
import urllib
import pickle
from datetime import date
from twit.api_wrapper import APIWrapper
from mlb.mlb_client import MLBClient
from arbitration.arbitrator import Arbitrator

#setup token params
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
refresh_token = os.environ.get("REFRESH_TOKEN")
redis_url = os.environ.get("REDIS_URL")
redirect_uri = os.environ.get("REDIRECT_URI")
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
r = redis.from_url(redis_url)
#redirect_uri = os.environ.get("REDIRECT_URI")
token_url = "https://api.twitter.com/2/oauth2/token"

def main():

    #need an oauth 1.0 token to get video upload access (these tokens should not expire)
    #get oauth1.0 access token to initiate both API versions
    access_token = r.get("mlb_tldr_auth1_access_token")
    access_secret = r.get("mlb_tldr_auth1_secret")
    reported = r.get("reported")
    reported = reported if reported else set()
    
    twitter = APIWrapper(consumer_key, consumer_secret, access_token, access_secret)
    mlb_client = MLBClient()

    arbitrator = Arbitrator(date.today(), reported, twitter, mlb_client)
    arbitrator.execute()

    postable_highlights = {}
    for game in games_today:
        gamePk = game['game_id']
        selected = None
        if game['status'] == "Final" and gamePk not in reported:
            highlights = statsapi.game_highlights(gamePk)
            #find a highlight to post
            for token in highlights.split("\n"):
                if "https" in token:
                    #this is a hack to get this video
                    selected = token
        postable_highlights[gamePk] = (selected, game['summary'])
    
    for k,v in postable_highlights.items():
        vid = requests.get(v[0])
        with open("highlight.mp4", 'wb') as f:
            f.write(vid.content)
        #returns a media object that we need the id of to post see here https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/entities#media
        media_id = apiv1.media_upload("highlight.mp4", media_category="tweet_video").media_id

        client.create_tweet(media_ids=[media_id], text=v[1]+" Highlight: ")
        reported.add(k)
        #client.create_tweet(text=v[1]+" Highlight: ")
        os.remove("highlight.mp4")

    r.set("reported", pickle.dumps(reported))

    # vid = requests.get("https://mlb-cuts-diamond.mlb.com/FORGE/2022/2022-10/05/d8a7c0c8-de293372-9f81e851-csvm-diamondx64-asset_1280x720_59_4000K.mp4")
    # with open("highlight.mp4",'wb') as f:
    #     # Saving received content as a png file in
    #     # binary format
    
    #     # write the contents of the response (r.content)
    #     # to a new file in binary mode.
    #     f.write(vid.content)
    
    # #initialize mlb client

    # #do some stuff
    # #upload test video
    # apiv1.media_upload("highlight.mp4", media_category="tweet_video")
    # os.remove("highlight.mp4")
    # os.remove("d8a7c0c8-de293372-9f81e851-csvm-diamondx64-asset_1280x720_59_4000K.mp4")

if __name__ == "__main__":
    main()
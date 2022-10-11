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
from src.twit.api_wrapper import APIWrapper
from src.mlb.mlb_client import MLBClient
from src.arbitration.arbitrator import Arbitrator

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
    if arbitrator.execute():
        #TODO: reset reported set every day
        #update reported in redis db
        r.set("reported", pickle.dumps(arbitrator.reported))
    else:
        print("No games left to report today")

if __name__ == "__main__":
    main()
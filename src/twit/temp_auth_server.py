# NOTE: STEPS TO AUTHORIZE FOR ACCOUNT FOR FIRST TIME/GENERATE NEW REFRESH TOKENS
#1.RUN THIS SCRIPT TO AND VISIT 127.0.0.1:5000/authorize 
#2.LOG IN WITH DESIRED BOT ACCOUNT
#3. REFRESH TOKEN WILL BE SET IN ENVIRON VAR.
#NOTE: Need to repeat for oauth1.0 for media upload, repeat steps with 127.0.0.1/5000/authorize1
#SIDENOTE: IF RUNNING THIS SCRIPT ON NON-LOCAL MACHINE, CALLBACK URI FOR APP WILL NEED TO BE CHANGED
#SEE THIS TUTORIAL FOR MORE DETAIL https://developer.twitter.com/en/docs/tutorials/creating-a-twitter-bot-with-python--oauth-2-0--and-v2-of-the-twi
#consumer api key feWJP76qBb57acBpUcjFztVXN
#consumer secret 29HoKzGUzC4tN9GwmtpScEX90Knf3xJ0szRx0Z0uYssdZkQVqE
# Authenticate to Twitter
import base64
import hashlib
import os
import re
import json
import requests
import redis
from requests.auth import AuthBase, HTTPBasicAuth
from requests_oauthlib import OAuth2Session, TokenUpdated
from flask import Flask, request, redirect, session, url_for, render_template
import tweepy

app = Flask(__name__)
app.secret_key = os.urandom(50)

client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
auth_url = "https://twitter.com/i/oauth2/authorize"
token_url = "https://api.twitter.com/2/oauth2/token"
redirect_uri = os.environ.get("REDIRECT_URI")
redis_url = os.environ.get("REDIS_URL")
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
r = redis.from_url(redis_url)
scopes = ["tweet.read", "users.read", "tweet.write", "offline.access"]

code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)

code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
code_challenge = code_challenge.replace("=", "")

oauth1_user_handler = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret,
    callback=redirect_uri)

def make_token():
    return OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)

def post_tweet(payload, token):
    print("Tweeting!")
    return requests.request(
        "POST",
        "https://api.twitter.com/2/tweets",
        json=payload,
        headers={
            "Authorization": "Bearer {}".format(token["access_token"]),
            "Content-Type": "application/json",
        },
    )
@app.route("/authorize2")
def authorize():
    global twitter
    twitter = make_token()
    authorization_url, state = twitter.authorization_url(
        auth_url, code_challenge=code_challenge, code_challenge_method="S256"
    )
    session["oauth_state"] = state
    return redirect(authorization_url)

@app.route("/authorize1")
def authorize1():
    return redirect(oauth1_user_handler.get_authorization_url(signin_with_twitter=True))

@app.route("/oauth/callback", methods=["GET"])
def callback():
    code = request.args.get("code")
    if code:
        #OAUTH2.0 FLOW
        token = twitter.fetch_token(
            token_url=token_url,
            client_secret=client_secret,
            code_verifier=code_verifier,
            code=code,
        )
        #save refresh token as env variable
        st_token = '"{}"'.format(token)
        j_token = json.loads(st_token)
        r.set("mlb_tldr_token", j_token)
        payload = {"text": "{}".format("Authorized")}
        #response = post_tweet(payload, token).json()
        return token
    #oauth1.0 flow
    access_token, access_token_secret = oauth1_user_handler.get_access_token(request.args.get("oauth_verifier"))
    r.set("mlb_tldr_auth1_access_token", access_token)
    r.set("mlb_tldr_auth1_secret", access_token_secret)
    return access_token

if __name__ == "__main__":
    app.run()
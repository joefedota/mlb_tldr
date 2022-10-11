#this should just replicate main with specific date and delete tweets after
import unittest
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
from datetime import datetime
from src.twit.api_wrapper import APIWrapper
from src.mlb.mlb_client import MLBClient
from src.arbitration.arbitrator import Arbitrator

class TestArbitrator(unittest.TestCase):

    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")
    redis_url = os.environ.get("REDIS_URL")
    consumer_key = os.environ.get("CONSUMER_KEY")
    consumer_secret = os.environ.get("CONSUMER_SECRET")
    r = redis.from_url(redis_url)
    token_url = "https://api.twitter.com/2/oauth2/token"
    test_ids = []

    def setUp(self):
        self.access_token = self.r.get("mlb_tldr_auth1_access_token")
        self.access_secret = self.r.get("mlb_tldr_auth1_secret")
        self.reported = set([715761, 715770])
        self.twitter = APIWrapper(self.consumer_key, self.consumer_secret, self.access_token, self.access_secret)
        self.mlb_client = MLBClient()
        self.arbitrator = Arbitrator(datetime.strptime("2022-10-07", "%Y-%m-%d"), self.reported, self.twitter, self.mlb_client)
    
    def test_download_highlight(self):
        self.arbitrator.download_highlight(715761, "https://mlb-cuts-diamond.mlb.com/FORGE/2022/2022-10/07/02c6db52-04a9f162-cd090b93-csvm-diamondx64-asset_1280x720_59_4000K.mp4")
        self.assertTrue(os.path.exists("715761.mp4"))
        os.remove("715761.mp4")

    def test_execute(self):
        resps = self.arbitrator.execute()
        self.assertEqual(len(resps), 2)
        self.assertFalse(resps[0].errors)
        self.assertFalse(resps[1].errors)
        self.test_ids.append(resps[0].data["id"])
        self.test_ids.append(resps[1].data["id"])
    
    def tearDown(self):
        for id in self.test_ids:
            self.twitter.clientv2.delete_tweet(id)
        

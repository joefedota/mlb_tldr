import unittest
import os
import redis
import tweepy

class APITestClass(unittest.TestCase):
    #this class is only designed to test to ensure our configuration is set up correctly to connect to the API
    #if something goes wrong in this test, you need to fix the environment configuration
    test_id = None
    def setUp(self):
        redis_url = os.environ.get("REDIS_URL")
        consumer_key = os.environ.get("CONSUMER_KEY")
        consumer_secret = os.environ.get("CONSUMER_SECRET")
        r = redis.from_url(redis_url)
        access_token = r.get("mlb_tldr_auth1_access_token")
        access_secret = r.get("mlb_tldr_auth1_secret")
        self.client = tweepy.Client(consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_secret)
        
        auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_secret)
        self.apiv1 = tweepy.API(auth)

    def test_basic_tweet(self):
        resp = self.client.create_tweet(text="Hello World!")
        self.test_id = resp.data["id"]
        self.assertFalse(resp.errors)
    
    def test_media_upload(self):
        #need a more comprehensive test for our media upload strategy, this is just to make sure we don't get
        #rejected for not having permission
        #get test resource path
        dirname = os.path.dirname(__file__)
        dirname = dirname[:len(dirname)-6] #minus the 6 chars for tests/
        
        media = self.apiv1.media_upload(os.path.join(dirname, "resources/highlight.mp4"), media_category="tweet_video")
        self.assertFalse(media.media_id == None)

    def tearDown(self):
        #must manually delete tweet if fails with error
        if self.test_id:
            self.client.delete_tweet(self.test_id)
    
    if __name__ == '__main__':
        unittest.main()
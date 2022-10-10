import tweepy

class APIWrapper:
    
    def __init__(self, consumer_key, consumer_secret, access_token, access_secret):
        self.clientv2 = tweepy.Client(consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_secret)
        auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_secret)
        self.cleintv1 = tweepy.API(auth)

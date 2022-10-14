class Tweet:
    content = ""
    def __init__(self, client, content):
        self.client = client
        self.content = content
    
    def post(self):
        self.client.clientv2.create_tweet(text=self.content)

class VideoTweet(Tweet):
    video = None
    def __init__(self, client, video, content):
        super().__init__(client, content)
        self.video = video
        self.media_id = None
        self.processing_info = None
    
    def prepare_video(self):
        self.media_id = self.client.clientv1.media_upload(self.video, media_category="tweet_video").media_id
        self.processing_info = self.client.clientv1.get_media_upload_status(self.media_id).processing_info
        while self.processing_info['state'] == 'pending':
            time.sleep(self.processing_info['check_after_secs'])
            self.processing_info = self.client.get_media_upload_status(self.media_id)
        if self.processing_info['state'] == 'succeeded':
            return True
        else:
            print("Error: {}".format(self.processing_info['processing_info']['error']['message']))
            return False

    def post(self):
        print("Success -- tweeting up a storm...")
        resp = self.client.clientv2.create_tweet(media_ids=[self.media_id], text=self.content)
        return resp

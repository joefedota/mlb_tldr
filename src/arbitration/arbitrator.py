from src.twit.posters import VideoTweet, Tweet
import os
import requests

class Arbitrator:
    #at a high level, the arbitrator should take in a twitter client, mlb (or general sport) api client and a
    #context in order to make decisions based on available data, and datetime / reported context
    
    def __init__(self, datetime, reported, twitter, data_client):
        self.datetime = datetime
        self.reported = reported
        self.twitter = twitter
        self.data_client = data_client
    
    def execute(self):
        #this will ideally use datetimes and different application states to determine what kind of data we want
        #for now we are just looking for game results of finished games we haven't reported
        print("Date passed to get_games: " + str(self.datetime))
        games_to_report = self.data_client.get_games(self.reported, self.datetime, "Final")
        if not games_to_report:
            return None
        games_to_report_pks = self.data_client.get_game_pks(games_to_report)
        highlights = self.data_client.get_highlights(games_to_report_pks)

        resps = []
        for game in games_to_report:
            #for now take first highlight from highlights list for each game
            game_pk = game['game_id']
            if len(highlights) < 1:
                tweet = Tweet(self.twitter, game["summary"])
                tweet.post()
                self.reported.add(game["game_id"])
            selected_highlight = highlights[game_pk][len(highlights[game_pk])-1]
            self.download_highlight(game_pk, selected_highlight[1])
            content = game["summary"] + "\n\nHighlight -- " + selected_highlight[0]
            tweet = VideoTweet(self.twitter, str(game_pk) + ".mp4", content)
            if tweet.prepare_video():
                resps.append(tweet.post())
                self.reported.add(game["game_id"])
            else:
                print("Error: could not post video")
            #either way delete video we just downloaded
            os.remove(str(game_pk) + ".mp4")

        return resps
    
    def download_highlight(self, game_pk, url):
        vid = requests.get(url)
        with open(str(game_pk) + ".mp4", 'wb') as f:
            f.write(vid.content)

from src.twit.posters import VideoTweet, Tweet
import os
import requests

class Arbitrator:
    #at a high level, the arbitrator should take in a twitter client, mlb (or general sport) api client and a
    #context in order to make decisions based on available data, and datetime / reported context
    #generate a set of baseball related highlight keywords


    def __init__(self, datetime, reported, twitter, data_client, keywords=[]):
        self.keywords = keywords
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
                resps.append(tweet.post())
                self.reported.add(game["game_id"])
            else:
                selected_highlight = self.highlight_selector(highlights[game_pk])
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
    
    def highlight_selector(self, highlights):
        #iterate through highlights and find latest timestamp highlight, best homerun, if there's a walkoff, etc
        #lets have a set of keywords we can look for in the blurb to determine what to post
        highest_rank = 0
        selected = None
        latest_timestamp = ""
        fallback = None
        for highlight in highlights:
            timestamp = highlight[2]
            rank = self.highlight_ranker(highlight)
            if rank > highest_rank:
                highest_rank = rank
                selected = highlight
            else:
                if not fallback or timestamp > latest_timestamp:
                    fallback = highlight
                    latest_timestamp = timestamp

        return selected if selected else fallback
    
    def highlight_ranker(self, highlight):
        #iterate through highlights and rank them based on keywords
        #highlight is of form (blurb, url, hence why we check highlight[0] for keyword)
        rank = 0
        normalized_blurb = highlight[0].lower()
        for keyword in self.keywords:
            if keyword[0] in normalized_blurb:
                rank += keyword[1]
        return rank

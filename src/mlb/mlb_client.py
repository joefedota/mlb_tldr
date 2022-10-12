import statsapi

class MLBClient:

    mlb_endpoint = "http://statsapi.mlb.com/api/v1/"

    def get_games(self, reported, date=None, status=None):
        games = statsapi.schedule(date.strftime("%Y-%m-%d"))
        filtered = []
        print("Reported games")
        print(reported)
        print(games)
        for game in games:
            if (not status or status == game["status"]) and not (game["game_id"] in reported):
                print("Adding game_pk " + str(game["game_id"]) + " to queue for tweeting.")
                filtered.append(game)
        return filtered
    
    def get_game_pks(self, games):
        game_pks = []
        for game in games:
            game_pks.append(game['game_id'])
        return game_pks
    
    def get_highlights(self, games_pks):
        postable_highlights = {}
        for game_pk in games_pks:
            selected = None
            highlights = statsapi.game_highlight_data(game_pk)
            if len(highlights) < 1:
                print("Error: " + str(game_pk) + " has no highlights")
            #return all highlight data and decide in arbitrator which to post
            tuples = []
            for highlight in highlights:
                #may need a check for playback availability in json response
                tuples.append((highlight['blurb'], highlight['playbacks'][0]['url']))
            #TODO -- replce tuples list with Highlight objects list
            postable_highlights[game_pk] = tuples
        return postable_highlights
    
    

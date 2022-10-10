import statsapi

class MLBClient:

    mlb_endpoint = "http://statsapi.mlb.com/api/v1/"

    def get_games(self, reported, date=None, status=None):
        games = statsapi.schedule(date.strftime("%Y-%m-%d"))
        filtered = []
        for game in games:
            if (not status or status == game["status"]) and not game["game_id"] in reported: 
                fitlered.append(game)
        return filtered
    
    def get_game_pks(self, reported, date=None, status=None);
        game_pks = []
        games = self.get_games(reported, date, status)
         for game in games:
            game_pks.append(game['game_id'])
        return game_pks
    
    def get_highlights(games_pks):
        postable_highlights = {}
        for game_pk in games_pks:
            selected = None
            highlights = statsapi.game_highlights(game_pk)
            #find a highlight to post
            for token in highlights.split("\n"):
                if "https" in token:
                    #this is a hack to get this video
                    selected = token
            postable_highlights[game_pk] = selected
    
    

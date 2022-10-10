class Arbitrator:
    #at a high level, the arbitrator should take in a twitter client, mlb (or general sport) api client and a
    #context in order to make decisions based on available data, and datetime / reported context
    
    def __init__(self, datetime, reported, twitter, data_client):
        self.datetime = datetime
        self.reported = reported
        self.twitter = twitter
        self.data_client = data_client
    
    def execute():
        #this will ideally use datetimes and different application states to determine what kind of data we want
        #for now we are just looking for game results of finished games we haven't reported
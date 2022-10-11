import unittest
import os
import statsapi
import src.mlb.mlb_client as mlb_client
from datetime import datetime

class TestMLBClient(unittest.TestCase):

    def setUp(self):
        self.client = mlb_client.MLBClient()
        self.reported = set([715761, 715770])

    def test_get_games(self):
        games = self.client.get_games(self.reported, date=datetime.strptime("2022-10-07", "%Y-%m-%d"), status="Final")
        self.assertEqual(len(games), 2)

    def test_get_highlights(self):
        games = self.client.get_games(self.reported ,date=datetime.strptime("2022-10-07", "%Y-%m-%d"), status="Final")
        game_pks = self.client.get_game_pks(games)
        highlights = self.client.get_highlights(game_pks)
        self.assertEqual(len(game_pks), 2)
        self.assertTrue(highlights[game_pks[0]][0] != None and highlights[game_pks[0]][1] != None)

    def tearDown(self):
        pass
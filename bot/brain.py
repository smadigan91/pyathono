'''
Created on Oct 30, 2017

@author: Sean
'''
from MathHelper import MathHelper
from ApiHelper import ApiHelper

api = ApiHelper("../auth.json", 136131, 1)
players = api.fetch_players({"status":"ALL", "sort":"AR"}, 500)
mh = MathHelper(players)
mh.rank_and_print_players(players=players, stats=[], weights={}, per_game=False, top_rank=500)
# stdev_map = player_stdev(players, ["PTS","REB","AST","STL","BLK","TOV"], False)
# rel_stdev(players[0], stdev_map, False)
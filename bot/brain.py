'''
Created on Oct 30, 2017

@author: Sean
'''
import MathHelper as mh
from ApiHelper import ApiHelper

api = ApiHelper("../auth.json", 136131, 1)
players = api.fetch_players({"status":"ALL", "sort":"AR"}, 400)
mh.rank_and_print_players(players, [], {"PTS":-1,"3PM":-1,"AST":-1,"STL":-1}, False, 300)
# stdev_map = player_stdev(players, ["PTS","REB","AST","STL","BLK","TOV"], False)
# rel_stdev(players[0], stdev_map, False)
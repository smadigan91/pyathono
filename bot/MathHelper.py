from ApiHelper import ApiHelper, all_cats, scoring_cats
from statistics import stdev, mean
from collections import defaultdict, OrderedDict
import operator
import math
'''
Created on Oct 14, 2017

@author: Sean
'''
#this should take in data structures returned by ApiHelper and calculate scores for players, potential targets, etc.

#calculate the standard deviation for a given set of players / set of stats
#uses all of a particular kind of categories by default
def player_std_dev(players, stats=[], pergame=True):
    stdv_mean_map = defaultdict(list)
    for player in players : 
        for stat in stats if stats else scoring_cats:
            stdv_mean_map[stat].append(player.get_pg_stat(stat) if pergame else player.get(stat))
    for stat, data in stdv_mean_map.items():
        stdv_mean_map[stat] = [round(stdev(data),3),round(mean(data),3)]
    return stdv_mean_map

def rel_std_dev(player, stdv_mean_map, pergame=True):
    player_score = defaultdict(list)
    for stat, dev_mean in stdv_mean_map.items():
        if pergame: player_score[stat] = round((player.get_pg_stat(stat) - dev_mean[1]) / dev_mean[0], 3)
        else: player_score[stat] = round((player.get(stat) - dev_mean[1]) / dev_mean[0], 3)
    return player_score

#just sums the standard deviations for whatever stats are given
def rank_players(players, stats=[], weights={}, pergame=True):
    score_map = {}
    stdev_map = player_std_dev(players, stats, pergame)
    for player in players:
        player_map = rel_std_dev(player, stdev_map, pergame)
        raw_score = simple_evaluate_player(player_map, stats) if not weights else weighted_evaluate_player(player, stdev_map, player_map, stats, weights) #Turnovers are bad
        diplay_key = "(" + str(player.get("AR")) + ") " + player.get("NAME") + " " + ", ".join("%s: %s" % item for item in player.get_total_stats().items())
        score_map[diplay_key] = raw_score
    score_map = OrderedDict(sorted(score_map.items(), key=operator.itemgetter(1), reverse=True))
#     print(score_map)
    pretty_print_ln(score_map, 50)
    
def simple_evaluate_player(player_map, stats=[]):
    return round(sum(player_map.values()) - round(2*player_map["TOV"],3) if "TOV" in stats else 0, 3) #Turnovers are bad

def weighted_evaluate_player(player, stdev_map, player_map, stats=[], weights={}):
    stats = stats if not stats else scoring_cats
    score = 0
    total = sum(x[0] for x in stdev_map.values())
    print(player.get("NAME"))
    print(player_map)
    for cat, stdev in player_map.items():
        #try and weigh the scalar by the amount of deviation
        scalar = 0 if cat not in weights else round(weights[cat]  * (1-stdev_map[cat][0]/total),3)
        score += (stdev * scalar) * (-1 if cat == "TOV" else 1)#turnovers are still bad
    return round(score,3)
        
    
#just for testing
def pretty_print(ugly, extra=""):
    print(extra + ', '.join("%s: %s" % item for item in ugly.items()))
    
def pretty_print_ln(ugly, top):
    rank=0
    for k,v in ugly.items() :
        rank+=1
        print(str(rank) + " " + k + ", SCORE:" + str(v))
        if rank == top: break
    
    
api = ApiHelper("../auth.json", 136131, 1)
players = api.fetch_players({"status":"ALL", "sort":"AR"}, 188)
# stdev_map = player_std_dev(players, ["PTS","REB","AST","STL","BLK","TOV"], False)
# rel_std_dev(players[0], stdev_map, False)
rank_players(players, scoring_cats, {"PTS":-1,"3PM":-1,"FT%":-5, "TOV":-1, "REB":3, "AST":3, "STL":3, "BLK":3, "FG%":1}, False)
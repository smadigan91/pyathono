from ApiHelper import ApiHelper, scoring_cats
from statistics import stdev, mean
from collections import defaultdict, OrderedDict
import operator
'''
Created on Oct 14, 2017

@author: Sean
'''

util_cats = ["FGA","FGM","FTA","FTM","3PA"]

#calculate the standard deviation for a given set of players / set of stats
#uses all of a particular kind of categories by default
def all_player_stdev(players, stats=[], pergame=True):
    stdv_mean_map = defaultdict(list)
    for player in players : 
        for stat in stats if stats else scoring_cats:
            stdv_mean_map[stat].append(player.get_pg_stat(stat) if pergame else player.get(stat))
    for stat, data in stdv_mean_map.items():
        stdv_mean_map[stat] = [round(stdev(data),3),round(mean(data),3)]
    return stdv_mean_map #for each stat, a tuple of the standard deviation and mean

def rel_stdev(player, stdv_mean_map, pergame=True):
    player_stdev = defaultdict(list)
    for stat, dev_mean in stdv_mean_map.items():
        if pergame:
            player_stdev[stat] = round((player.get_pg_stat(stat) - dev_mean[1]) / dev_mean[0], 3)#TODO average per game stats
        else:
            base = (player.get(stat) - dev_mean[1])
            if stat == "FG%":
                player_stdev[stat] = round(base * player.get("FGA") * dev_mean[0],3)
            elif stat == "FT%":
                player_stdev[stat] = round(base * player.get("FTA") * dev_mean[0],3)
            else :
                player_stdev[stat] = round(base / dev_mean[0], 3)
    player.stdev_map = player_stdev #map of player stat cats to  player standard deviation relative to league per cat

def simple_eval_player(player, stats=[]):
    player.score = round(sum([val for key, val in player.stdev_map.items() if key not in util_cats]) - round(2*player.stdev_map["TOV"],3) if "TOV" in stats else 0, 3) #Turnovers are bad

def weighted_eval_player(player, stdev_map, stats=[], weights={}):
    stats = stats if not stats else scoring_cats
    total_score = 0
    score_map = {}
    total = sum(x[0] for x in stdev_map.values())
#     print(player.get("NAME"))
#     print(player_map)
    for cat, stdev in player.stdev_map.items():
        #try and weigh the scalar by the amount of deviation
        scalar = 0 if cat not in weights else round(weights[cat]  * (1-stdev_map[cat][0]/total),3)
        should_omit = cat in weights and weights[cat] <= 0 or cat in util_cats #omit mades and attempts
        score = 0 if should_omit else stdev + (stdev * scalar)
        if cat == "TOV" : score = score*-1
        score_map[cat] = round(score,3)
        total_score += score
    player.score = round(total_score,3)
    player.score_map = score_map


#just sums the standard deviations for whatever stats are given
def rank_players(players, stats=[], weights={}, pergame=True):
    stats = scoring_cats if not stats else stats
    score_map = {}
    stdev_map = all_player_stdev(players, stats, pergame)
    for player in players:
        rel_stdev(player, stdev_map, pergame)
        simple_eval_player(player, stats) if not weights else weighted_eval_player(player, stdev_map, stats, weights)
        score_map[player] = player.score
    score_map = OrderedDict(sorted(score_map.items(), key=operator.itemgetter(1), reverse=True))
    return score_map

def rank_and_print_players(players, stats=[], weights={}, pergame=True, topRank=None):
    topRank = 50 if topRank is None else topRank
    score_map = rank_players(players, stats, weights, pergame)
    pretty_print_player_map(score_map, topRank) # return something eventrually
    
    
def pretty_print_player_map(player_map, top):
    rank=0
    for player in player_map.keys() :
        rank+=1
        player.pretty_print(player.stdev_map if not player.score_map else player.score_map, rank)
        if rank == top: break
    
    
# api = ApiHelper("../auth.json", 136131, 1)
# players = api.fetch_players({"status":"ALL", "sort":"AR"}, 400)
# rank_players(players, [], {"FT%":-1, "TOV":-1}, False)
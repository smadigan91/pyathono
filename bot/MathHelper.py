from ApiHelper import scoring_cats
from statistics import stdev, mean
from collections import defaultdict, OrderedDict
import operator

util_cats = ["FGA","FGM","FTA","FTM"]
#list of idealized values for calculation of relative stdev, ripping from bballmonster
#they seem to help improve the rankings vs. using the league average in certain cases
ideal_FGP = 0.472
ideal_FTP = 0.797

BLK_SCAL = 1.9
REB_SCAL = 1.3
FT_SCAL = 1.12
FG_SCAL = 1.5
TPM_SCAL = 1.25
STL_SCAL = 1.2
PTS_SCAL = 2.4
AST_SCAL = 1.15
TOV_SCAL = 1.1

class MathHelper:
    
    pkey_total_score_index = {}
    player_total_score_index = {}
    
    pkey_pg_score_index = {}
    player_pg_score_index = {}
    
    def __init__(self, players):
        self.players = players
        
    #calculate the standard deviation for a given set of players / set of stats
    #uses all of a particular kind of category by default
    def all_player_stdev(self, players, stats=[], per_game=True):
        stdv_mean_map = defaultdict(list)
        for player in players : 
            for stat in stats if stats else scoring_cats:
                if per_game :
                    if stat in ["FG%","FT%"]: stdv_mean_map[stat].append(player.get(stat))
                    else: stdv_mean_map[stat].append(player.get_pg_stat(stat))
                else: stdv_mean_map[stat].append(player.get(stat))
        for stat, data in stdv_mean_map.items():
            stdv_mean_map[stat] = [round(stdev(data),5),round(mean(data),5)]
        return stdv_mean_map #for each stat, a tuple of the standard deviation and mean for the entire league
    
    def rel_stdev(self, player, stdv_mean_map, per_game=True):
        player_stdev = defaultdict(list)
        for stat, dev_mean in stdv_mean_map.items():
            if per_game:
                if stat == "FG%":
                    base = (player.get(stat) - ideal_FGP)
                    player_stdev[stat] = round(base * player.get_pg_stat("FGA") * 1.7,5)
                elif stat == "FT%":
                    base = (player.get(stat) - ideal_FTP)
                    player_stdev[stat] = round(base * player.get_pg_stat("FTA") * 3.2,5)
                elif stat == "3PM":
                    base = (player.get_pg_stat(stat) - dev_mean[1]*1.8)
                    player_stdev[stat] = round(base / dev_mean[0], 3)
                elif stat == "PTS":
                    base = (player.get_pg_stat(stat) - dev_mean[1]*1.85)
                    player_stdev[stat] = round(base / dev_mean[0], 3)
                elif stat == "AST":
                    base = (player.get_pg_stat(stat) - dev_mean[1]*1.85)
                    player_stdev[stat] = round(base / dev_mean[0], 3)
                elif stat == "TOV":
                    base = (player.get_pg_stat(stat) - dev_mean[1]*1.75)
                    player_stdev[stat] = round(base / dev_mean[0], 3)
                elif stat == "STL":
                    base = (player.get_pg_stat(stat) - dev_mean[1]*1.7)
                    player_stdev[stat] = round(base / dev_mean[0], 3)
                elif stat == "BLK":
                    base = (player.get_pg_stat(stat) - dev_mean[1]*1.6)
                    player_stdev[stat] = round(base / dev_mean[0], 3)
                else :
                    player_stdev[stat] = round((player.get_pg_stat(stat) - dev_mean[1]) / dev_mean[0], 3)
            else:
                if stat == "FG%":
                    base = (player.get(stat) - ideal_FGP)
                    player_stdev[stat] = round(base * player.get("FGA") * dev_mean[0],5)
                elif stat == "FT%":
                    base = (player.get(stat) - ideal_FTP)
                    player_stdev[stat] = round(base * player.get("FTA") * dev_mean[0],5)
                elif stat == "3PM":
                    base = (player.get(stat) - dev_mean[1]*1.8) #the hard-coded scalars here slightly amplify the league average for this cat
                    player_stdev[stat] = round(base / dev_mean[0], 3)
                elif stat == "PTS":
                    base = (player.get(stat) - dev_mean[1]*1.85) #a smaller scalar means the player's relative "score" will increase, and vice versa
                    player_stdev[stat] = round(base / dev_mean[0], 3)
                elif stat == "AST":
                    base = (player.get(stat) - dev_mean[1]*1.85) #sort of a coarser control valve in comparison to the scalars applied at the end
                    player_stdev[stat] = round(base / dev_mean[0], 3)
                elif stat == "TOV":
                    base = (player.get(stat) - dev_mean[1]*1.75) #and yes they're all totally arbitrary
                    player_stdev[stat] = round(base / dev_mean[0], 3)
                elif stat == "STL":
                    base = (player.get(stat) - dev_mean[1]*1.7)
                    player_stdev[stat] = round(base / dev_mean[0], 3)
                elif stat == "BLK":
                    base = (player.get(stat) - dev_mean[1]*1.6)
                    player_stdev[stat] = round(base / dev_mean[0], 3)
                else :
                    player_stdev[stat] = round((player.get(stat) - dev_mean[1]) / dev_mean[0], 5)
        if per_game: player.pg_stdev_map = player_stdev #map of player stat cats to  player standard deviation relative to league per cat
        else: player.total_stdev_map = player_stdev
    
    def simple_eval_player(self, player, stats=[]):
        player.score = round(sum([val for key, val in player.stdev_map.items() if key not in util_cats]) - round(2*player.stdev_map["TOV"],3) if "TOV" in stats else 0, 5)
    
    def weighted_eval_player(self, player, stdev_map, per_game=True, stats=[], weights={}):
        stats = stats if not stats else scoring_cats
        total_score = 0
        score_map = {}
        total = sum(x[0] for x in {k:v for k, v in stdev_map.items() if k not in util_cats}.values())
        for cat, stdev in player.pg_stdev_map.items() if per_game else player.total_stdev_map.items():
            #try and weigh the scalar by the relative deviation for this cat
            scalar = 1-(stdev_map[cat][0]/total)
            #these scalars are just a last step to "polish" the numbers to more closely resemble values for other ranking sites lol im such a hack
            if cat == "BLK" : scalar /= BLK_SCAL
            elif cat == "REB" : scalar /= REB_SCAL
            elif cat == "3PM" : scalar /= TPM_SCAL
            elif cat == "AST" : scalar /= AST_SCAL
            elif cat == "FG%" : scalar /= FG_SCAL
            elif cat == "FT%" : scalar /= FT_SCAL
            elif cat == "STL" : scalar *= STL_SCAL
            elif cat == "TOV" : scalar *= TOV_SCAL
            elif cat == "PTS" : scalar *= PTS_SCAL
            if weights:
                scalar *= weights[cat] if cat in weights else 1
                should_omit = (cat in weights and weights[cat] <= 0) or cat in util_cats #omit mades and attempts
            else :
                should_omit = cat in util_cats
                
            score = 0 if should_omit else stdev + (stdev * scalar)
            if cat == "TOV" : score = score*-1
            score_map[cat] = round(score/2,2)
            total_score += round(score/2,2)
        if per_game:
            player.pg_score_map = score_map
            player.pg_score_map["OVR"] = round(total_score/10,3)
        else:
            player.total_score_map = score_map
            player.total_score_map["OVR"] = round(total_score/10,3)
    
    
    #just sums the standard deviations for whatever stats are given
    #indexes: {player_key : score_map}, {player_key : total_score} hmm should I just combine them
    def rank_players(self, players, stats=[], weights={}, per_game=True):
        stats = scoring_cats if not stats else stats
        score_map = {}
        stdev_map = self.all_player_stdev(players, stats, per_game)
        for player in players:
            self.rel_stdev(player, stdev_map, per_game)
            self.weighted_eval_player(player, stdev_map, per_game, stats, weights)
            score_map[player] = player.get_score(per_game)
        score_map = OrderedDict(sorted(score_map.items(), key=operator.itemgetter(1), reverse=True))
        pkey_score_index = {k.get("PKEY") : v for k, v in score_map.items()}
        if per_game:
            self.player_pg_score_index = score_map
            self.pkey_pg_score_index = pkey_score_index
        else:
            self.player_total_score_index = score_map
            self.pkey_total_score_index = pkey_score_index
        return score_map
    
    def rank_and_print_players(self, players, stats=[], weights={}, per_game=True, top_rank=None):
        top_rank = 50 if top_rank is None else top_rank
        score_map = self.rank_players(players, stats, weights, per_game)
        self.pretty_print_player_map(score_map, top_rank, per_game) # return something eventually
        
        
    def pretty_print_player_map(self, player_map, top, per_game=True):
        rank=0
        for player in player_map.keys() :
            rank+=1
            player.pretty_print(player.pg_score_map if per_game else player.total_score_map, rank)
    #         player.pretty_print_rank_name_only(rank)
            if rank == top: break
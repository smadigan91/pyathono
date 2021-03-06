from yahoo_oauth import OAuth2
import xml.etree.ElementTree as ET
from collections import defaultdict
import re
import ScheduleHelper
from constraint import *

base_url = "https://fantasysports.yahooapis.com/fantasy/v2"

league_idt = ".l.{lid}"
team_idt = league_idt + ".t.{tid}"

base_league_url = base_url + "/league/nba" + league_idt
base_team_url = base_url + "/team/nba" + team_idt
base_player_url = base_url + "/player/"
base_players_url = base_url + "/players"
base_league_players_url = base_league_url + "/players;" #assumes params

all_cats = [
    "AR",
    "NAME",
    "PKEY",
    "GP",
    "FGA",
    "FGM",
    "FG%",
    "FTA",
    "FTM",
    "FT%",
    "3PA",
    "3PM",
    "3P%",
    "PTS",
    "REB",
    "AST",
    "STL",
    "BLK",
    "TOV"
    ]

scoring_cats = [x for x in all_cats if x not in ["AR","NAME","PKEY","GP","3P%","3PA"]]

#idk why but when using this library this stupid thing is prefixed to each xml tag
xmlprefix = "{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}"

def l_url(l_id):
    return base_league_url.format(lid=l_id)

def t_url(l_id, t_id):
    return base_team_url.format(lid=l_id, tid=t_id)

def p_url(p_k):
    return base_player_url + p_k

def ps_url(l_id):
    return base_league_players_url.format(lid=l_id)

def get_team_idt(self, tid):
        return team_idt.format(lid=self.league_id, tid=tid)

#xml prefix
def xmlp(text):
    return xmlprefix + text

#xml prefix multilevel
def xmlp_multi(text):
        return text.replace('/','/{0}').format(xmlprefix)
    
def find(element, search):
    return element.find(xmlp(search))

def find_multi(element, search):
    return element.find(xmlp_multi(search))

def find_all(element, search):
    return element.findall(search.replace('//', '//{0}').format(xmlprefix))

def ok_get(response):
        code = response.status_code
        if not code is 200:
            raise Exception("status code was {0}".format(code))
        return response
    
#return 0.0 if a % value isn't present
def format_pct(xml_val, prec):
        return 0.0 if xml_val is "-" else round(float(xml_val), prec)
    
def format_stat(xml_val):
    return 0 if (xml_val is None or xml_val == "-") else int(xml_val)

class ApiHelper:
    
    #league metadata
    l_meta = {
        "num_teams": 0,
        "num_pos": 0
        }
    
    def __init__(self, authFileName, leagueId, teamId):
        self.league_id = leagueId
        self.team_id = teamId
        self.req = OAuth2(None, None, from_file=authFileName).session
        self.index_league_metadata()
        
    #TODO return convenient data structures
    
    def default_maxrank(self):
        return self.l_meta["num_teams"]*self.l_meta["num_pos"]
    
    def get(self, url, params={}):
        return ok_get(self.req.get(url, params=params))
    
    '''
    LEAGUE
    '''
    
    def fetch_league(self):
        response = self.get(l_url(self.league_id))
        print(response.text)
        
    def index_league_metadata(self):
        response = self.get(l_url(self.league_id) + "/settings")
        league_settings = ET.fromstring(response.text)
        self.l_meta["num_teams"] = int(find_multi(league_settings, './league/num_teams').text)
        for roster_position in find_multi(league_settings, './league/settings/roster_positions'):
            if find(roster_position, 'position').text != "IL":
                self.l_meta["num_pos"] +=  int(find(roster_position, 'count').text)
                
    '''
    TEAM
    '''
        
    
    def fetch_team(self, tid=None, params={}):
        tid = tid if tid is not None else self.team_id
        response = self.get(t_url(self.league_id, tid), params=params)
        print(response.text)
        
    def fetch_roster(self, tid=None, params={}):
        tid = tid if tid is not None else self.team_id
        response = self.get(t_url(self.league_id, tid) + "/roster", params=params)
        print(response.text)
    
    '''
    PLAYERS
    '''
    
    # map of {player_name : player_key}
    def fetch_roster_players(self, tid=None, params={}):
        tid = tid if tid is not None else self.team_id
        response = self.get(t_url(self.league_id, tid) + "/roster/players", params=params)
        print(response.text)
        players = find_all(ET.fromstring(response.text), './/player')
        roster_players = []
        for xml_player in players:
            roster_players.append(RosterPlayer(xml_player))
        return roster_players
    
    def fetch_healthy_roster(self, tid=None, params={}):
        tid = tid if tid is not None else self.team_id
        players = self.fetch_roster_players(tid, params)
        healthy_players = [p for p in players if not p.injured]
        return healthy_players
    
    def calculate_lineup_combos(self, healthy_players):
        problem = Problem()
        position_map = defaultdict(list)
        current_position_counts = {}
        current_roster_positions = []
        for player in healthy_players:
            if player.POS not in current_position_counts:
                current_roster_positions.append(player.POS)
                current_position_counts[player.POS] = 0
            else:
                current_position_counts[player.POS] += 1
                enumpos = player.POS + str(current_position_counts[player.POS]+1)
                current_roster_positions.append(enumpos)
            for pos in player.positions:
                position_map[pos].append(player.NAME)
        for position in current_roster_positions:
            problem.addVariable(position, position_map[re.sub(r'\d+', '', position)])
        
        problem.addConstraint(AllDifferentConstraint())
        solutions = problem.getSolutions()
        
        #for each solution in solutions
        #sum up the total value (pergame or not - specify) for each non-BN position and assign that lineup a score
        #put (lineup, score) in a new dict
        #put that new dict in an OrderedDict, order by value descending
        #return top n lineups by score
        
        #to get the best lineups given today's players:
        #make sure you calculate the "value" of a player that scores a 0 in every cat for that day
        #fill each eligible position pool with all players playing that are eligible PLUS the "0" guy
        #sort same way as above
        #when assigning the roster, after moving around the players who are actually playing, assign everyone else to the bench (probably easiest)
        #or I guess just leave everyone else where they were, idk
        
    def fetch_player_stats(self, player_key, params={}):
        response = self.get(p_url(player_key) + "/stats",params=params)
        print(response.text)
        
    def fetch_player_stats_by_season(self, player_key, season, params={}):
        response = self.get(p_url(player_key) + "/stats;type=season;season={0}".format(season),params=params)
        print(response.text)
        
    def fetch_players_stats(self, player_keys = []):
        players = []
        #iterate through chunks of 25 player keys, that's the max yahoo will return at once
        for pk_chunk in [player_keys[x:x+25] for x in range(0, len(player_keys),25)] :
            pks = ""
            for pk in pk_chunk:
                pks += pk + ","
            pks = pks[:-1] + ";"
            response = self.get(base_players_url + ";player_keys=" + pks + "out=stats")
            players.extend(find_all(ET.fromstring(response.text), './/player'))
        
        return players
    
    '''
    fetches the top 'count' players per the given criteria.
    Yahoo doesn't make it easy to fetch advanced stats, so we need to fetch the top ranked players
    within the league context, index their player ids, and then re-fetch all of them outside of the
    league context which is where advanced stats can be found.
    '''
    def fetch_players(self, params = {}, count=None):
        start = 0
        count = count if (count is not None or count <=1) else 25
        url = ps_url(self.league_id) + "start={0};count={1};"
        players = []
        for k, v in params.items():
            url += k + "=" + str(v) + ";"
        url = url[:-1]#trim last ;
        
        response = self.get(url.format(start, 25 if count > 25 else count))
        for player in find_all(ET.fromstring(response.text), './/player') :
            players.append(find(player, 'player_key').text)
        
        while count > 25:
            start +=25
            count -=25
            response = self.get(url.format(start, 25 if count > 25 else count))
            for player in find_all(ET.fromstring(response.text), './/player') :
                players.append(find(player, 'player_key').text)
        
        return self.format_players(self.fetch_players_stats(players))
    
    #only return players who have played games
    def format_players(self, xml_players):
        all_players = []
        for index, xml_player in enumerate(xml_players):
            stats = find_all(xml_player, './/stat')
            gp = format_stat(stats[0][1].text)
            if gp > 0:
                all_players.append(Player(xml_player, stats, index+1))
        return all_players
            
        #def fetch_all_rosterable_players(self, num_teams, num_ros_spots):
        #should fetch the top players by actual rank
    
class RosterPlayer:
    
    def __init__(self, player):
        self.NAME = find(player, 'name')[0].text
        self.PKEY = find(player, 'player_key').text
        self.POS = find(player, 'selected_position')[2].text
        self.positions = []
        for position in find(player, 'eligible_positions'):
            self.positions.append(position.text)
        self.positions.append('BN')
        self.injured = 'IL' in self.positions
        self.team_full = find(player, 'editorial_team_full_name').text
        

class Player:
    '''
    0 GP    Games Played
    1 GS    Games Started
    2 MIN    Minutes Played
    ### 3 MPG    Minutes Played Per Game / they don't send this one :(
    3 FGA    Field Goals Attempted
    4 FGM    Field Goals Made
    5 FG%    Field Goals Percentage
    6 FTA    Free Throws Attempted
    7 FTM    Free Throws Made
    8 FT%    Free Throws Percentage
    9 3PA    3-point Shots Attempted
    10 3PM    3-point Shots Made
    11 3PP    3-point Shots Percentage
    12 PTS    Points Scored
    13 OREB    Offensive Rebounds
    14 DREB    Defensive Rebounds
    15 REB    Total Rebounds
    16 AST    Assists
    17 ST    Steals
    18 BLK    Blocked Shots
    19 TOV    Turnovers
    20 A/T    Assist/Turnover Ratio
    21 PF    Personal Fouls
    22 DISQ    Times Fouled Out
    23 TECH    Technical Fouls
    24 EJCT    Ejections
    25 FF      Flagrant Fouls
    '''
    def __init__(self, player, stats, rank):
        self.AR = rank
        self.NAME = find(player, 'name')[0].text
        self.PKEY = find(player, 'player_key').text
        self.total_stats = { #there might be a sexier way to do this but im lazy sorry
            "AR": rank,
            "NAME": self.NAME,
            "PKEY": self.PKEY,
            "GP": int(stats[0][1].text),
            "FGA": format_stat(stats[3][1].text),
            "FGM": format_stat(stats[4][1].text),
            "FG%": format_pct(stats[5][1].text, 3),
            "FTA": format_stat(stats[6][1].text),
            "FTM": format_stat(stats[7][1].text),
            "FT%": format_pct(stats[8][1].text, 3),
            "3PA": format_stat(stats[9][1].text),
            "3PM": format_stat(stats[10][1].text),
            "3P%": format_pct(stats[11][1].text, 3),
            "PTS": format_stat(stats[12][1].text),
            "REB": format_stat(stats[15][1].text),
            "AST": format_stat(stats[16][1].text),
            "STL": format_stat(stats[17][1].text),
            "BLK": format_stat(stats[18][1].text),
            "TOV": format_stat(stats[19][1].text)
            }
        self.pg_stats = {k: (self.div_gp(v) if self.total_stats["GP"] > 0 else 0) for k, v in self.total_stats.items() if k in scoring_cats}
        self.total_stdev_map = {} #raw
        self.total_score_map = {"OVR":0} #weighted
        self.pg_stdev_map = {}
        self.pg_score_map = {"OVR":0} #weighted
        
    def get(self, stat):
        return self.total_stats[stat]
    
    def get_score(self, pergame=True):
        return self.pg_score_map["OVR"] if pergame else self.total_score_map["OVR"]
    
    def get_score_map(self, pergame=True):
        return self.pg_score_map if pergame else self.total_score_map
    
    def get_stats(self, stats=[]):
        results = {}
        for stat in stats :
            results[stat] = self.total_stats[stat]
        
    def get_pg_stat(self, stat):
        return self.pg_stats[stat]
    
    def get_pg_stats(self, stats = []):
        return {k:v for k, v in self.pg_stats.items() if k in stats}
    
    def get_total_stats(self):
        return {k:v for k, v in self.total_stats.items() if k in scoring_cats}
    
    def get_scored_stats(self, omit, weights=[], pergame=True):
        score_map = {}
        if pergame:
            if not self.pg_score_map:
                score_map = {k:v for k, v in self.pg_stdev_map.items() if k not in omit}
            else:
                if not weights:
                    score_map = {k:v for k, v in self.pg_score_map.items() if k not in omit}
                else:
                    score_map = {k:v for k, v in self.pg_score_map.items() if k in weights}
        else:
            if not self.total_score_map:
                score_map = {k:v for k, v in self.total_stdev_map.items() if k not in omit}
            else:
                if not weights:
                    score_map = {k:v for k, v in self.total_score_map.items() if k not in omit}
                else:
                    score_map = {k:v for k, v in self.total_score_map.items() if k in weights}
        return {k:v for k, v in score_map.items()}
        
    
    def div_gp(self, stat, prec=3):
        return round(float(stat / self.total_stats["GP"]),prec) if isinstance(stat, int) else stat
        
    def pretty_print(self, stat_map, rank=None): 
        print(((str(rank) + " ") if rank is not None else "") + ("("+str(self.get("AR"))+") " + self.get("NAME") + ", ") + (', '.join("%s: %s" % item for item in stat_map.items())))

    def pretty_print_rank_name_only(self, rank=None, pergame=True):
        print(((str(rank) + " ") if rank is not None else "") + ("("+str(self.get("AR"))+") " + self.get("NAME") + ", ") + ("" if self.get_score(pergame) == 0 else ("OVR: " + str(self.get_score(pergame)))))

        
#testing
api = ApiHelper("../auth.json", 136131, 1)
healthy_players = api.fetch_healthy_roster()
api.calculate_lineup_combos(healthy_players)

# for player in api.fetch_players({"status":"ALL", "sort":"AR"}, 150):
#     player.pretty_print()
    

# ids = api.fetch_roster_player_ids()
# print(ids)
# api.fetch_player_stats(list(ids.values())[0])
# api.fetch_player_stats_by_season(ids['Stephen Curry'], 2017)
# api.fetch_players_stats(ids.values())
# api.fetch_players_stats(ids.values())
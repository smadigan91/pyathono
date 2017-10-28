from yahoo_oauth import OAuth2
import xml.etree.ElementTree as ET

#find a better way to do uri templating lol this is gross v

league_idt = ".l.{lid}"
team_idt = league_idt + ".t.{tid}"
base_league_url = "https://fantasysports.yahooapis.com/fantasy/v2/league/nba.l.{lid}"
base_team_url = "https://fantasysports.yahooapis.com/fantasy/v2/team/nba"
base_player_url = "https://fantasysports.yahooapis.com/fantasy/v2/player/"

#idk why but when using this library this stupid thing is prefixed to each xml tag
xmlprefix = "{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}"

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

def ok_get(response):
        code = response.status_code
        if not code is 200:
            raise Exception("status code was {0}".format(code))

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
        
    #TODO return convenient data structures
    
    def fetch_league(self):
        response = self.req.get(base_league_url.format(lid=self.league_id))
        ok_get(response)
        print(response.text)
        
    def index_league_metadata(self):
        response = self.req.get(base_league_url.format(lid=self.league_id) + "/settings")
        league_settings = ET.fromstring(response.text)
        self.l_meta["num_teams"] = int(find_multi(league_settings, './league/num_teams').text)
        for roster_position in find_multi(league_settings, './league/settings/roster_positions'):
            if find(roster_position, 'position').text != "IL":
                self.l_meta["num_pos"] +=  int(find(roster_position, 'count').text)
        
    
    def fetch_team(self, tid=None, params={}):
        tid = tid if tid is not None else self.team_id
        response = self.req.get(base_team_url + self.get_team_idt(tid), params=params)
        ok_get(response)
        print(response.text)
        
    def fetch_roster(self, tid=None, params={}):
        tid = tid if tid is not None else self.team_id
        response = self.req.get(base_team_url + self.get_team_idt(tid) + "/roster", params=params)
        ok_get(response)
        print(response.text)
        
    # map of {player_name : player_key}
    def fetch_roster_players(self, tid=None, params={}):
        tid = tid if tid is not None else self.team_id
        response = self.req.get(base_team_url + self.get_team_idt(tid) + "/roster/players", params=params)
        ok_get(response)
        players = ET.fromstring(response.text)
        ids = {}
        for player in find_multi(players, './team/roster/players'):
            ids[find(player, 'name')[0].text] = find(player, 'player_key').text
        return ids
        
    def fetch_player_stats(self, player_key, params={}):
        response = self.req.get(base_player_url + player_key + "/stats",params=params)
        ok_get(response)
        print(response.text)
        
    def fetch_player_stats_by_season(self, player_key, season, params={}):
        response = self.req.get(base_player_url + player_key + "/stats;type=season;season={0}".format(season),params=params)
        ok_get(response)
        print(response.text)
        
    def fetch_players_stats(self, player_keys = [], params = {}):
        pks = "player_keys="
        for pk in player_keys:
            pks += pk + ","
        pks = pks[:-1] + ";"
        print(base_league_url + "/players;player_keys=" + pks + "out=stats")
        response = self.req.get(base_league_url + "/players;player_keys=" + pks + "out=stats",params=params)
        ok_get(response)
        print(response.text)
        
#     def fetch_all_rosterable_players(self, num_teams, num_ros_spots):
        #should fetch the top players by actual rank
        
    def get_team_idt(self, tid):
        return team_idt.format(lid=self.league_id, tid=tid)
        
    #TODO convenience APIs

#testing
api = ApiHelper("../auth.json", 136131, 1)
# api.fetch_league()
# api.fetch_team()
# api.fetch_roster()
ids = api.fetch_roster_players()
print(ids)
api.index_league_metadata()
# api.fetch_player_stats(list(ids.values())[0])
# api.fetch_player_stats_by_season(ids['Stephen Curry'], 2017)
# api.fetch_players_stats(ids.values())
# api.fetch_player_stats(ids[0])
from yahoo_oauth import OAuth2
import json
import xml.etree.ElementTree as ET

"""if not oauth.token_is_valid():
    oauth.refresh_access_token()"""
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
    
    league_idt = ".l.{lid}"
    team_idt = league_idt + ".t.{tid}"
    base_league_url = "https://fantasysports.yahooapis.com/fantasy/v2/league/nba"
    base_team_url = "https://fantasysports.yahooapis.com/fantasy/v2/team/nba"
    base_player_url = "https://fantasysports.yahooapis.com/fantasy/v2/player/"
    
    def __init__(self, jsonFileName):
        self.user_props = json.loads(open('../' + jsonFileName).read())
        self.league_id = self.user_props["league_id"]
        self.team_id = self.user_props["team_id"]
        self.base_league_url += self.league_idt.format(lid=self.league_id)
        self.req = OAuth2(None, None, from_file='../' + jsonFileName).session
        
    #TODO return convenient data structures
    
    def fetch_league(self, params={}):
        response = self.req.get(self.base_league_url, params=params)
        ok_get(response)
        print(response.text)
    
    def fetch_team(self, tid=None, params={}):
        tid = tid if tid is not None else self.team_id
        response = self.req.get(self.base_team_url + self.get_team_idt(tid), params=params)
        ok_get(response)
        print(response.text)
        
    def fetch_roster(self, tid=None, params={}):
        tid = tid if tid is not None else self.team_id
        response = self.req.get(self.base_team_url + self.get_team_idt(tid) + "/roster", params=params)
        ok_get(response)
        print(response.text)
        
    # map of {player_name : player_key}
    def fetch_roster_players(self, tid=None, params={}):
        tid = tid if tid is not None else self.team_id
        response = self.req.get(self.base_team_url + self.get_team_idt(tid) + "/roster/players", params=params)
        ok_get(response)
        players = ET.fromstring(response.text)
        ids = {}
        for player in find_multi(players, './team/roster/players'): #0=root#13=roster3=players
            ids[find(player, 'name')[0].text] = find(player, 'player_key').text
        return ids
        
    def fetch_player_stats(self, player_key, params={}):
        response = self.req.get(self.base_player_url + player_key + "/stats",params=params)
        ok_get(response)
        print(response.text)
        
    def fetch_player_stats_by_season(self, player_key, season, params={}):
        response = self.req.get(self.base_player_url + player_key + "/stats;type=season;season={0}".format(season),params=params)
        ok_get(response)
        print(response.text)
        
    def fetch_players_stats(self, player_keys = [], params = {}):
        pks = "player_keys="
        for pk in player_keys:
            pks += pk + ","
        pks = pks[:-1] + ";"
        print(self.base_league_url + "/players;player_keys=" + pks + "out=stats")
        response = self.req.get(self.base_league_url + "/players;player_keys=" + pks + "out=stats",params=params)
        ok_get(response)
        print(response.text)
        
    def get_team_idt(self, tid):
        return self.team_idt.format(lid=self.league_id, tid=tid)
        
    #TODO convenience APIs

#testing
api = ApiHelper("auth.json")
# api.fetch_league()
# api.fetch_team()
# api.fetch_roster()
ids = api.fetch_roster_players()
print(ids)
# api.fetch_player_stats(list(ids.values())[0])
api.fetch_player_stats_by_season(ids['Stephen Curry'], 2016)
# api.fetch_players_stats(ids.values())
# api.fetch_player_stats(ids[0])
from yahoo_oauth import OAuth2
import xml.etree.ElementTree as ET

#find a better way to do uri templating lol this is gross v
base_url = "https://fantasysports.yahooapis.com/fantasy/v2"

league_idt = ".l.{lid}"
team_idt = league_idt + ".t.{tid}"

base_league_url = base_url + "/league/nba" + league_idt
base_team_url = base_url + "/team/nba" + team_idt
base_player_url = base_url + "/player/"
base_players_url = base_league_url + "/players;" #assumes params

#idk why but when using this library this stupid thing is prefixed to each xml tag
xmlprefix = "{http://fantasysports.yahooapis.com/fantasy/v2/base.rng}"

def l_url(l_id):
    return base_league_url.format(lid=l_id)

def t_url(l_id, t_id):
    return base_team_url.format(lid=l_id, tid=t_id)

def p_url(p_k):
    return base_player_url + p_k

def ps_url(l_id):
    return base_players_url.format(lid=l_id)

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
        self.index_league_metadata()
        
    #TODO return convenient data structures
    
    '''
    LEAGUE
    '''
    
    def fetch_league(self):
        response = self.req.get(l_url(self.league_id))
        ok_get(response)
        print(response.text)
        
    def index_league_metadata(self):
        response = self.req.get(l_url(self.league_id) + "/settings")
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
        response = self.req.get(t_url(self.league_id, tid), params=params)
        ok_get(response)
        print(response.text)
        
    def fetch_roster(self, tid=None, params={}):
        tid = tid if tid is not None else self.team_id
        response = self.req.get(t_url(self.league_id, tid) + "/roster", params=params)
        ok_get(response)
        print(response.text)
    
    '''
    PLAYERS
    '''
    
    # map of {player_name : player_key}
    def fetch_roster_players(self, tid=None, params={}):
        tid = tid if tid is not None else self.team_id
        response = self.req.get(t_url(self.league_id, tid) + "/roster/players", params=params)
        ok_get(response)
        players = ET.fromstring(response.text)
        ids = {}
        for player in find_multi(players, './team/roster/players'):
            ids[find(player, 'name')[0].text] = find(player, 'player_key').text
        return ids
        
    def fetch_player_stats(self, player_key, params={}):
        response = self.req.get(p_url(player_key) + "/stats",params=params)
        ok_get(response)
        print(response.text)
        
    def fetch_player_stats_by_season(self, player_key, season, params={}):
        response = self.req.get(p_url(player_key) + "/stats;type=season;season={0}".format(season),params=params)
        ok_get(response)
        print(response.text)
        
    def fetch_players_stats(self, player_keys = [], params = {}):
        pks = "player_keys="
        for pk in player_keys:
            pks += pk + ","
        pks = pks[:-1] + ";"
        print(ps_url(self.league_id) + "player_keys=" + pks + "out=stats")
        response = self.req.get(base_league_url + "/players;player_keys=" + pks + "out=stats",params=params)
        ok_get(response)
        print(response.text)
        
    def fetch_players(self, params = {}):
        url = ps_url(self.league_id)
        for k, v in params.items():
            url += k + "=" + v + ";"
        url = url[:-1]#trim last ;
        print(url)
        response = self.req.get(url)
        ok_get(response)
        return response.text
        
#     def fetch_all_rosterable_players(self, num_teams, num_ros_spots):
        #should fetch the top players by actual rank
        
    #TODO convenience APIs

#testing
api = ApiHelper("../auth.json", 136131, 1)
# api.fetch_league()
# api.fetch_team()
# api.fetch_roster()
ids = api.fetch_roster_players()
print(ids)
print(api.fetch_players({"status":"ALL", "sort":"AR"}))
# api.fetch_player_stats(list(ids.values())[0])
# api.fetch_player_stats_by_season(ids['Stephen Curry'], 2017)
# api.fetch_players_stats(ids.values())
# api.fetch_player_stats(ids[0])
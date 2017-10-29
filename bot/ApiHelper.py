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

def find_all(element, search):
    return element.findall(search.replace('//', '//{0}').format(xmlprefix))

def ok_get(response):
        code = response.status_code
        if not code is 200:
            raise Exception("status code was {0}".format(code))
        return response

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
        players = ET.fromstring(response.text)
        ids = {}
        for player in find_all(players, './/player'):
            ids[find(player, 'name')[0].text] = find(player, 'player_key').text
        return ids
        
    def fetch_player_stats(self, player_key, params={}):
        response = self.get(p_url(player_key) + "/stats",params=params)
        print(response.text)
        
    def fetch_player_stats_by_season(self, player_key, season, params={}):
        response = self.get(p_url(player_key) + "/stats;type=season;season={0}".format(season),params=params)
        print(response.text)
        
    def fetch_players_stats(self, player_keys = [], params = {}):
        pks = "player_keys="
        for pk in player_keys:
            pks += pk + ","
        pks = pks[:-1] + ";"
        print(ps_url(self.league_id) + "player_keys=" + pks + "out=stats")
        response = self.get(base_league_url + "/players;player_keys=" + pks + "out=stats",params=params)
        print(response.text)
    
    #count is separate
    def fetch_players(self, params = {}, count=None):
        start = 0
        count = count if (count is not None or count <=1) else 25
        url = ps_url(self.league_id) + "start={0};count={1};"
        for k, v in params.items():
            url += k + "=" + str(v) + ";"
        url = url[:-1]#trim last ;
        
        response = self.get(url.format(start, 25 if count > 25 else count))
        players = find_all(ET.fromstring(response.text), './/player')
        
        while count > 25:
            start +=25
            count -=25
            response = self.get(url.format(start, 25 if count > 25 else count))
            players.extend(find_all(ET.fromstring(response.text), './/player'))
        
        return players
        
                
            
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
print(len(api.fetch_players({"status":"ALL", "sort":"AR"}, 73)))
# api.fetch_player_stats(list(ids.values())[0])
# api.fetch_player_stats_by_season(ids['Stephen Curry'], 2017)
# api.fetch_players_stats(ids.values())
# api.fetch_player_stats(ids[0])
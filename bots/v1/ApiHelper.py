from yahoo_oauth import OAuth2
import json

"""if not oauth.token_is_valid():
    oauth.refresh_access_token()"""


class ApiHelper:
    
    league_idt = ".l.{lid}"
    team_idt = league_idt + ".t.{tid}"
    player_idt = ".p.{pid}"
    base_league_url = "https://fantasysports.yahooapis.com/fantasy/v2/league/nba"
    base_team_url = "https://fantasysports.yahooapis.com/fantasy/v2/team/nba"
    
    def __init__(self, jsonFileName, oauth):
        self.user_props = json.loads(open('../' + jsonFileName + '.json').read())
        self.league_id = self.user_props["league_id"]
        self.team_id = self.user_props["team_id"]
        self.base_league_url += self.league_idt.format(lid=self.league_id)
        self.req = oauth.session
        
    #TODO return convenient data structures
    
    def fetch_league(self, params={}):
        response = self.req.get(self.base_league_url.format(leagueID=self.league_id), params=params)
        print(response.text)
    
    def fetch_team(self, tid=None, params={}):
        tid = tid if tid is not None else self.team_id
        response = self.req.get(self.base_team_url + self.get_team_idt(tid), params=params)#
        print(response.text)
        
    def fetch_roster(self, tid=None, params={}):
        tid = tid if tid is not None else self.team_id
        response = self.req.get(self.base_team_url + self.get_team_idt(tid) + "/roster", params=params)
        print(response.text)
        
    def fetch_roster_players(self, tid=None, params={}):
        tid = tid if tid is not None else self.team_id
        response = self.req.get(self.base_team_url + self.get_team_idt(tid) + "/roster/players", params=params)
        print(response.text)
        
    def get_team_idt(self, tid):
        return self.team_idt.format(lid=self.league_id, tid=tid)
        
    #TODO convenience APIs

#testing
oauth = OAuth2(None, None, from_file='../auth.json')
api = ApiHelper("saucebauce",oauth)
api.fetch_league()
api.fetch_team()
api.fetch_roster()

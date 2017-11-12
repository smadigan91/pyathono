import csv
from datetime import datetime as dt

def get_todays_teams():
    mydate = dt.now()
    today_date_key = mydate.strftime("%b %d %Y")
    return get_teams_playing_on(today_date_key)

def get_teams_playing_on(date_key):
    teams = []
    with open('../2017_2018_nba_remaining_schedule.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            if row[0] == str(date_key):
                teams.append(row[1])
                teams.append(row[2])
    return teams
# pyathono
python + yahoo

# Useful Links

### Yahoo Stuff

To register your app with yahoo (to get the consumer key/secret) you can go [here](https://developer.yahoo.com/apps/create/). You'll need a domain to register a web app. I'm just using a desktop app for now while I test this so I can just run it from the command line.

[Yahoo Sports API documentation](https://developer.yahoo.com/fantasysports/guide/GettingStarted.html)

### Libraries

[yahoo_oauth](https://pypi.org/project/yahoo_oauth/) - handles all the annoying oauth shit (required)

[requests](http://docs.python-requests.org/en/master/user/advanced/) - the library that handles REST stuff for the oauth library yahoo_oauth is using, helpful for understanding how to make different kinds of requests with it

[xml](https://docs.python.org/2/library/xml.etree.elementtree.html) - library I'm using to parse xml

[json](https://dzone.com/articles/python-reading-json-file) - tutorial on using the 'json' library (though it's as easy as you'd think)

# Usage

## Setup

1) Register your app with yahoo by following the link up in `Yahoo Stuff`

2) Follow the steps for setting up the auth.json file in the yahoo_oauth documentation. You just need to send an initial request and it'll prompt you to visit some yahoo site, click some button, then your auth.json file should be populated and look similar to the one im already using

3) If you're writing another module that uses ApiHelper within this project, you can use it like so:

```
from v1 import ApiHelper
api = ApiHelper("../auth.json", 136131, 1)
```

where 136131 and 1 are a valid leagueId and teamId corresponding to a yahoo account whose app credentials live in auth.json. These two numbers are https://basketball.fantasysports.yahoo.com/nba/{leagueId}/{teamId} when you click "My Team" in one of the yahoo fantasy leagues you're in.

## Ranking Players

Fetching the top `n` ranked players in a given league sorted by player score is easy once you have your auth stuff set up. Assuming you've constructed an instance of the ApiHelper as shown above, here are some examples of interesting commands to use:

1) **`players = api.fetch_players({"status":"ALL", "sort":"AR"}, 500)`**

The call to `fetch_players` takes in two parameters - the parameter map, and the number of players to fetch and rank (`n`) respectively. 
The parameter map can/should contain parameters per Yahoo's player collection / instance documentation, [which can be found here](https://developer.yahoo.com/fantasysports/guide/players-collection.html). Note that this will only rank players who have played in at least one game, so if you pass in `500` but only  `400` have played games, it will only fetch and rank the top 400 players. 500 is a nice safe upper bound for including all players who have played, I've found.

The number of ranked players is important. If you're using a small number for `n`, it's going to fetch the top `n` ranked players and use those players for ranking evaluation, meaning it will only rank those players relative to each other, not the entire league. This can result in some interesting ranking anomalies, so I would recommend using a higher number for `n` if possible, as doing so might include players like Dwight Howard who are ranked terribly in a league context but might have a much higher ranking if you choose to punt certain categories.

2) **`MathHelper.rank_and_print_players(players, [], {}, False, 500)`**

The `MathHelper` class ingests players returned by the `ApiHelper` class and ranks them. This API call specifically will take in a set of players returned by `ApiHelper` and print the top `500` ranked players, or just every player who has played in at least one game (as of this moment 417). Again, I'm just using 500 as a safe upper bounds.

Aside from the list of players and the number to print, this API takes in an optional list `[]` and a dict `{}`.

The `list` can be a list of stat categories to calculate the rankings for, inclusive. If it's empty, MathHelper will use `["FGA","FGM","FG%","FTA","FTM","FT%","3PA","3PM","PTS","REB","AST","STL","BLK","TOV"]` which is all of the stats the bot will actually take into consideration. If you want to customize the categories that are scored, you must specify a subset of this list - no stats outside of what's in this list are taken into consideration. (**Note** that `FGA, FGM, FTA, and FTM` aren't directly factored into a player's score, but rather are used to help calculate a player's `FG%` and `FT%` score respectively.)

The `dict` can be a mapping of categories to score weight. Punts are specified by giving a category a weight of `-1` (any negative value would provide the same functionality), and weights by giving a category a value greater than `1`. For example, if I pass in `{"PTS":-1,"3PM":-1,"AST":-1,"STL":2}`, scores for PTS, 3PM and AST will not be counted, and scores for STL will be doubled. Passing in an empty dict will evaluate all category scores for a player normally.

The `boolean` in-between the dict and the number of players to print denotes whether or not the players should be evaluated by their per game values. Currently I don't have that implemented, so I'm just calling it with `False` every time, but that should be implemented shortly.

Currently I'm executing everything in `brain.py`, which I'm using as my driver class, so feel free to do the same.

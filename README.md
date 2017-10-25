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

1) Register your app with yahoo by following the link up in `Yahoo Stuff`

2) Follow the steps for setting up the auth.json file in the yahoo_oauth documentation. You just need to send an initial request and it'll prompt you to visit some yahoo site, click some button, then your auth.json file should be populated and look similar to the one im already using

3) If you're writing another module that uses ApiHelper within this project, you can use it like so:

```
from v1 import ApiHelper
api = ApiHelper("../auth.json", 136131, 1)
```

where 136131 and 1 are a valid leagueId and teamId corresponding to a yahoo account whose app credentials live in auth.json. These two numbers are https://basketball.fantasysports.yahoo.com/nba/{leagueId}/{teamId} when you click "My Team" in one of the yahoo fantasy leagues you're in.

# Note
I haven't written in anything but java in years, so this code probably looks pretty stupid if you're used to something scriptier like python - for example I'm checking every single response with an exception-handling-wrapper method (ok_get), and that feels pretty retarded. There's a lot of refactoring that'll need to be done here and I'll get to it eventually as I get re-familiarized with python, so bear with me

# pyathono
python + yahoo

# Useful Links

### Yahoo Stuff

To register your app with yahoo (to get the consumer key/secret) you can go [here](https://developer.yahoo.com/apps/create/). You'll need a domain to register a web app - I'm just using a desktop app for now while I test this so I can just run it from the command line.

[Yahoo Sports API documentation](https://developer.yahoo.com/fantasysports/guide/GettingStarted.html)

### Libraries

[yahoo_oauth](https://pypi.org/project/yahoo_oauth/) - handles all the annoying oauth shit (required)

[requests](http://docs.python-requests.org/en/master/user/advanced/) - the library that handles REST stuff for the oauth library yahoo_oauth is using, helpful for understanding how to make different kinds of requests with it

[xml](https://docs.python.org/2/library/xml.etree.elementtree.html) - library I'm using to parse xml

[json](https://dzone.com/articles/python-reading-json-file) - tutorial on using the 'json' library (though it's as easy as you'd think)

# Usage

1) Follow the steps for setting up the auth.json file in the yahoo_oauth documentation. You just need to send an initial request and it'll prompt you to visit some yahoo site, click some button, then your auth.json file should be populated and look similar to the one im already using

2) Once your auth.json file looks pretty, you can create a json file with the league / team ID corresponding to a yahoo account you own (my trial run was with saucebauce.json). Or you could do something else, this is just how I'm doing it

3) If you in fact did not do something else and followed #2, all you need to do to use the ApiHelper is:

```
oauth = OAuth2(None, None, from_file='../auth.json')
api = ApiHelper("saucebauce",oauth)
```

and you're ready to start fetching some xml.

# Note
I haven't written in anything but java in years, so this code probably looks pretty stupid if you're used to something scriptier like python - for example I'm checking every single response with an exception-handling-wrapper method (ok_get), and that feels pretty retarded. There's a lot of refactoring that'll need to be done here and I'll get to it eventually as I get re-familiarized with python, so bear with me

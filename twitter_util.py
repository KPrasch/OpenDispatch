from apps.people.auth import get_oauth
import requests
import json


def listen_to_twitter():
    oauth = get_oauth()

    # Open the request via the twitter stream API for only the Twitter account to collect from.
    twitter_follow_id = "951808694"
    url = "https://stream.twitter.com/1.1/statuses/filter.json?follow={0}".format(twitter_follow_id)

    r = requests.get(url=url, auth=oauth, stream=True)

    for line in r.iter_lines():
        if line:
            d = json.loads(line)
            d

    print("Crosstown Traffic Thread Listening for Tweets ...")
    return r.iter_lines

listen_to_twitter()

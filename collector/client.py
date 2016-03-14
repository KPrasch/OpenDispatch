import requests
from apps.people.auth import get_oauth

from twisted.logger import Logger

from collector.object_store_backend import COLLECTOR_BACKEND

log = Logger()


def start_twitter_stream_request():
    """
    Opens a connection the Twitter API and receives tweets for the specified User, pushing each tweet into incident extrapolation
    """

    # Check if the Server is Authenticated with Twitter, and get oauth token.
    oauth = get_oauth()

    # Open the request via the twitter stream API for only the Twitter account to collect from.
    twitter_follow_id = "951808694"
    url = "https://stream.twitter.com/1.1/statuses/filter.json?follow={0}".format(twitter_follow_id)

    response = requests.get(url=url, auth=oauth, stream=True)

    log.info("Crosstown Traffic Thread Listening for Tweets ...")
    return response


def store_stream(theReactor, stream_response):
    for tweet in stream_response.iter_lines():
        COLLECTOR_BACKEND.push(tweet)

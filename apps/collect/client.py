import logging
import json

from twisted.python.threadpool import ThreadPool
from twisted.internet.threads import deferToThreadPool
from twisted.internet import reactor
import requests
from dateutil import parser

from apps.collect.views import process_import
from apps.people.auth import get_oauth, setup_oauth

auth_logger = logging.getLogger('auth')
default_logger = logging.getLogger('django')


API_CLIENT_THREADPOOL = ThreadPool(name='API Client ThreadPool.')
API_CLIENT_THREADPOOL.start()


def stream_twitter():
    """
    Opens a connection the Twitter API and receives tweets for the specified User, pushing each tweet into incident extrapolation
    """

    # Check if the Server is Authenticated with Twitter, and get oauth token.
    oauth = get_oauth()

    # Open the request via the twitter stream API for only the Twitter account to collect from.
    twitter_follow_id = "951808694"
    url = "https://stream.twitter.com/1.1/statuses/filter.json?follow={0}".format(twitter_follow_id)

    r = requests.get(url=url, auth=oauth, stream=True)

    default_logger.info("Crosstown Traffic Thread Listening for Tweets ...")
    return r.iter_lines


def handle_twitter_stream_event(event):
    event = json.loads(event)
    payload = event["text"]
    twitter_time = event["created_at"]
    # Get twitter's tweet-received time.
    received_datetime = parser.parse(twitter_time)
    # Now, do it.
    process_import(payload, received_datetime)
    return payload, received_datetime


def main(theReactor):
    stream_iterator = stream_twitter()

    # Blocks Thread
    for tweet in stream_iterator():

        d = deferToThreadPool(theReactor, API_CLIENT_THREADPOOL, handle_twitter_stream_event, tweet)
        d.addCallback(process_import)
        yield d

if __name__ == "__main__":
    main(reactor)

"""
# filter out keep-alive new lines
if line:

"""
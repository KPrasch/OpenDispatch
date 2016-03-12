import logging
from urlparse import parse_qs

from twisted.python.threadpool import ThreadPool
from twisted.internet.threads import deferToThreadPool, deferToThread
from twisted.internet import reactor
from requests_oauthlib import OAuth1
import requests
import json
from dateutil import parser
from apps.collect.views import process_import

from private.secret_settings import *

auth_logger = logging.getLogger('auth')
default_logger = logging.getLogger('django')


API_CLIENT_THREADPOOL = ThreadPool(name='API Client ThreadPool.')
API_CLIENT_THREADPOOL.start()


def setup_oauth():
    """Authorize your app via identifier."""
    # Request token
    oauth = OAuth1(TWITTER_CONSUMER_KEY, client_secret=TWITTER_CONSUMER_SECRET)
    r = requests.post(url=TWITTER_REQUEST_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)

    resource_owner_key = credentials.get('oauth_token')[0]
    resource_owner_secret = credentials.get('oauth_token_secret')[0]

    # Authorize
    authorize_url = TWITTER_AUTHORIZE_URL + resource_owner_key
    auth_logger.error('Please go here and authorize: ' + authorize_url)

    verifier = raw_input('Please input the verifier: ')
    oauth = OAuth1(TWITTER_CONSUMER_KEY,
                   client_secret=TWITTER_CONSUMER_SECRET,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret,
                   verifier=verifier)

    # Finally, Obtain the Access Token
    r = requests.post(url=TWITTER_ACCESS_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)
    token = credentials.get('oauth_token')[0]
    secret = credentials.get('oauth_token_secret')[0]

    return token, secret


def get_oauth():
    oauth = OAuth1(TWITTER_CONSUMER_KEY,
                   client_secret=TWITTER_CONSUMER_SECRET,
                   resource_owner_key=TWITTER_OAUTH_TOKEN,
                   resource_owner_secret=TWITTER_OAUTH_TOKEN_SECRET)
    return oauth


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
    return None


def main(theReactor):
    stream_iterator = stream_twitter()

    for tweet in stream_iterator():

        yield deferToThreadPool(theReactor, API_CLIENT_THREADPOOL, handle_twitter_stream_event, tweet)


if __name__ == "__main__":
    main(reactor)

"""
# filter out keep-alive new lines
if line:

"""
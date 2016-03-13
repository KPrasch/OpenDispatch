from urlparse import parse_qs
import logging

import requests
from requests_oauthlib import OAuth1

from private.secret_settings import *

auth_logger = logging.getLogger('auth')


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

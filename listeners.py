from datetime import datetime

import tweepy


class TwitterStreamListener(tweepy.StreamListener):

    def __init__(self, collector, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collector = collector

    def on_status(self, status):
        self.collector.buffer.put(data=status, source='twitter', agency=status.author.screen_name)

    def on_error(self, status_code):
        if status_code == 420:
            return False



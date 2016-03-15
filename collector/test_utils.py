import json
import os
from settings import BASE_DIR
from collector.bulletin import BulletinTweet, StringBulletin


class FakeBulletinStream(object):

    def __init__(self, condition='good'):
        self.condition = condition
        self.status_code = 200

    def iter_lines(self):

        if self.condition is 'good':
            with open(os.path.join(BASE_DIR, 'sample_twitter_stream.txt'), 'r') as f:
                self.last_stream_item = f.readline()

        elif self.condition is 'bad':
            self.last_stream_item = '{"text": "incident dict", "created_at": "July 2nd, 1983."}'

        yield self.last_stream_item


class FakeBulletinFactory(object):
    """
    Yields a bulletin
    """
    def __init__(self, bulletin_class=StringBulletin, condition='good'):
        self.stream = FakeBulletinStream(condition)
        self.bulletin_class = bulletin_class
        self._iterator = self.stream.iter_lines()

    def __iter__(self):
        for line in self._iterator:
            yield self.bulletin_class(line)

    def next(self):
        return self.bulletin_class(self._iterator.next())



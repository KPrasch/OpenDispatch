import json


class FakeTwitterStream(object):

    def __init__(self, bulliten, condition='good'):
        self.condition = condition
        self.status_code = 200
        self.last_stream_item = bulliten

    def iter_lines(self):
        yield self.last_stream_item


class FakeBulletin(object):

    def __init__(self, condition='good'):
        if condition is 'good':
            with open('../sample_twitter_stream.txt', 'r') as f:
                self.bulletin = f.readline()

        elif condition is 'bad':
            self.bulletin = json.dumps({"text": "incident dict", "created_at": "July 2nd, 1983."})

        elif condition is 'alright':
            self.bulletin = json.dumps({"text": "incident dict", "created_at": "November, 8th, 1990"})

    def twitter(self):
        return FakeTwitterStream(self.bulletin)

    def generic(self):
        return json.loads(self.bulliten)['text']

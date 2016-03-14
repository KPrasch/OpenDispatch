from collections import deque


class CollectorBackend(object):

    def __init__(self):
        self._dq = deque()

    def push(self, collected):
        return self._dq.appendleft(collected)

    def pop(self):
        return self._dq.pop()


COLLECTOR_BACKEND = CollectorBackend()
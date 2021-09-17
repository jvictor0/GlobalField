import time
import threading
import bisect

class PositionQueueElem:
    def __init__(self, timestamp, pattern_id, relative_position):
        self.timestamp = timestamp
        self.pattern_id = pattern_id
        self.relative_position = relative_position

    def __le__(self, other):
        return self.timestamp <= other.timestamp

    def __lt__(self, other):
        return self.timestamp < other.timestamp

class PositionQueue:
    def __init__(self, retention=2.0):
        self.queue = []
        self.retention = retention
        self.lock = threading.Lock()

    def GC(self):
        with self.lock:
            self.GCNoLock()

    def GCNoLock(self):
        now = time.time()
        ix = 0
        while len(self.queue) > ix and self.queue[ix].timestamp + self.retention < now:
            ix += 1
        self.queue = self.queue[ix:]

    def Add(self, elems):
        with self.lock:
            for elem in elems:
                self.queue.append(elem)
            self.GCNoLock()

    def Get(self):
        with self.lock:
            now = time.time()
            now_elem = PositionQueueElem(now, None, None)
            ix = bisect.bisect_left(self.queue, now_elem)
            if ix > 0:
                return self.queue[ix - 1]
            else:
                return PositionQueueElem(None, None, None)

    

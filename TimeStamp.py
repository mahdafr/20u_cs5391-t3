class TimeStamp:
    def __init__(self, now):
        self._START = now
        self._last_sent = None

    def message(self, sndr, rcvr, now):
        if not self._elapsed(now):
            return None
        self._last_sent = now
        return '{0}\t{1}\t{2}\t{3}'.format(sndr, rcvr, str(now.date()), str(now.time()))

    """ Is it time to send a message (10ms since last_sent)? """
    def _elapsed(self, now, time=10000):                        # 1000 microseconds in a ms, so 10,000 for 10ms
        if self._last_sent is None:
            self._last_sent = now
        return (now - self._last_sent).microseconds >= time

    """ Is it time to close the thread (5m since START)? """
    def finished(self, now, time=300):                          # 60s in a minute, 300s in 5 minutes
        return (now - self._START).seconds >= time

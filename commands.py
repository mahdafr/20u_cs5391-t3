host = '127.0.0.1'
port = 8080
s_cmd = 'SERVERADDR'
g_cmd = 'GETPEERS'
test = 'TEST'
fack = 'FILEREC'
fstart = 'FILESTART'
fend = 'FILEEND'
sep = ', '
doub = ')'
TAB = '\t'
COLON = ':'
LEFT = '['
RIGHT = ']'
remove = [LEFT, RIGHT, '\"', '\'']


def parse(s):
    s = s[len(s_cmd) + 1:-1].split(sep)                         # remove the command
    if doub in s[1]:
        return s[0] + COLON + s[1].split(doub)[0]               # in case multiple commands got bundled together
    return s[0] + COLON + s[1]


def get_pl_and_ts(s):                                               # convert the message to a peer list and timestamp
    pl, ts = _split(s)
    return _clean(pl), ts


def _split(s):
    return _get_pl(s), _get_ts(s)


def _get_ts(msg):                                                   # get the timestamp out of the string
    if COLON not in msg or (msg[0] == LEFT and msg[-1] == RIGHT):
        return ''
    ts = msg
    if LEFT in ts:
        if ts[-1] == RIGHT:                                         # to left of '['
            ts = ts[:ts.index(LEFT)-1]
        if ts[0] == LEFT:                                           # to right of ']'
            ts = ts[ts.index(RIGHT)+1:]
    return ts


def _get_pl(msg):                                                   # get the peer list out of the string
    if LEFT in msg:
        return msg[msg.index(LEFT)+1:msg.index(RIGHT)-1]
    return ''


def _clean(pl):                                                     # convert the string to list of (addr:port) tuples
    if pl != '':
        for r in remove:
            pl = pl.replace(r, '')
        pl = pl.split(sep)                                          # separate the peer addresses
        for i in range(len(pl)):                                    # convert into (str, int) tuples
            tmp = pl[i].split(COLON)
            pl[i] = (str(tmp[0]), int(tmp[1]))
    return pl


def drop_commands_for_ts(msg):                                      # drop commands in TimeStamp, if any
    msg = msg.replace(g_cmd, '')
    msg = msg.replace(s_cmd, '')
    return msg


def wants_peers(msg):                                               # client asked to send peer list
    return g_cmd in msg


def got_server(msg):                                                # client asked to save listener address
    return s_cmd in msg


def to_string(addr):
    return str(addr[0] + ':' + str(addr[1]))                        # 'ip_addr:port'


def is_same_addr(a, b):                                             # (host, port) so Clients don't connect to self
    return a[0] == b[0] and a[1] == b[1]


def clean(msg):                                                     # command to test whether connection is still active
    return msg.replace(test, '')


def client_to_str(c_list):                                          # convert the list of Peers to a str for sending
    return str(c_list)


s_cmd = 'SERVERADDR'
g_cmd = 'GETPEERS'
ack = 'OKAY'
sep = ', '
split_col = ':'
doub = ')'
split_msg = '\t'
remove = ['[', ']', '\"']


def parse(s):
    s = s[len(s_cmd) + 1:-1].split(sep)
    if doub in s[1]:
        return s[0] + split_col + s[1].split(doub)[0]               # in case multiple commands got bundled together
    return s[0] + split_col + s[1]


def to_address(s):
    s.split(split_col)
    return s[0], int(s[1])


def to_list(s):
    for r in remove:
        s = s.replace(r, '')
    s = s.split(sep)
    print(s)
    return s


def parse_addr(s):
    return s.split(split_msg)[0]


def can_write_to_file(msg):
    return g_cmd not in msg and s_cmd not in msg                    # write to file if not receiving commands


def send_peers(msg):
    return g_cmd in msg                                             # client asked to send peer list


def get_server(msg):
    return s_cmd in msg                                             # client asked to save listener address


def server_ackd(msg):
    return ack in msg

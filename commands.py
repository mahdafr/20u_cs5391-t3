host = '127.0.0.1'
s_cmd = 'SERVERADDR'
g_cmd = 'GETPEERS'
test = 'TEST'
fack = 'FILEREC'
fstart = 'FILESTART'
fend = 'FILEEND'
sep = ', '
split_col = ':'
doub = ')'
split_msg = '\t'
remove = ['[', ']', '\"', '\'']


def parse(s):
    s = s[len(s_cmd) + 1:-1].split(sep)
    if doub in s[1]:
        return s[0] + split_col + s[1].split(doub)[0]               # in case multiple commands got bundled together
    return s[0] + split_col + s[1]


def to_address(s):
    s.split(split_col)
    return s[0], int(s[1])


def to_list(s):
    for r in remove:                                                # clean the string
        s = s.replace(r, '')
    ret = s.split(sep)
    for i in range(len(ret)):
        tmp = ret[i].split(split_col)
        ret[i] = (str(tmp[0]), int(tmp[1]))
    return ret


def parse_addr(s):                                                  # if list has extra data, drop the extra data
    return s.split(split_msg)[0]


def can_write_to_file(msg):
    return g_cmd not in msg and s_cmd not in msg                    # write to file if not receiving commands


def send_peers(msg):
    return g_cmd in msg                                             # client asked to send peer list


def get_server(msg):
    return s_cmd in msg                                             # client asked to save listener address


def to_string(addr):
    return str(addr[0] + ':' + str(addr[1]))                        # 'ip_addr:port'


def is_same_addr(a, b):                                             # (host, port)
    return a[0] == b[0] and a[1] == b[1]


def clean(msg):
    return msg.replace(test, '')

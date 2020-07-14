host = '127.0.0.1'
port = 8080
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
    print('before mods', s)
    for r in remove:                                                # clean the string
        s = s.replace(r, '')
    print('after replace', s)
    ret = s.split(sep)
    print('after split', s)
    for i in range(len(ret)):
        tmp = ret[i].split(split_col)
        ret[i] = (str(tmp[0]), int(tmp[1]))
    print('after loop', ret)
    return ret


def parse_addr(s):                                                  # if list has extra data, drop the extra data
    return s.split(split_msg)[0]


def to_file(msg):
    msg = msg.replace(g_cmd, '')                                    # drop commands in TimeStamp
    msg = msg.replace(s_cmd, '')
    return msg


def send_peers(msg):
    return g_cmd in msg                                             # client asked to send peer list


def got_server(msg):
    return s_cmd in msg                                             # client asked to save listener address


def to_string(addr):
    return str(addr[0] + ':' + str(addr[1]))                        # 'ip_addr:port'


def is_same_addr(a, b):                                             # (host, port)
    return a[0] == b[0] and a[1] == b[1]


def clean(msg):
    return msg.replace(test, '')


def client_to_str(c_list):
    return str(c_list)


import socket, threading, datetime
from TimeStamp import TimeStamp

client = []
s_cmd = 'SERVERADDR'
cmd = 'GETPEERS'


class CThread(threading.Thread):
    def __init__(self, c_sock, c_addr, file='out/serverTimeData.txt'):
        threading.Thread.__init__(self)                         # create a new thread
        self._socket = c_sock
        self._addr = c_addr
        self._socket.setblocking(0)                             # non-blocking mode
        print('Client has connected at address:\t', self._addr)
        self._ts = TimeStamp(datetime.datetime.now())
        self._file = open(file, 'a')

    """ Send a TimeStamp, if it is time to do so. """
    def _send(self):
        msg = self._ts.message(self._addr, socket.gethostbyname(socket.gethostname()), datetime.datetime.now())
        if msg is not None:
            try:
                self._socket.sendall(bytes(msg, 'UTF-8'))           # time to send the TimeStamp
                self._file.write(msg + '\n')                        # write the TimeStamp to file
            except ConnectionAbortedError:
                print('Client has disconnected from:\t', self._addr)
                return -1
            except ConnectionResetError:
                print('Client has forcibly disconnected from:\t', self._addr)
                return -1
        return 0

    """ Receive a TimeStamp, if it has been sent, without blocking the thread. """
    def _receive(self, buff_size=2048):
        try:
            msg = self._socket.recv(buff_size).decode()
            if cmd not in msg or s_cmd not in msg:
                self._file.write(msg + '\n')                        # write the TimeStamp to file
            else:
                if s_cmd in msg:
                    client.append(list(msg[len(s_cmd)+1:]))         # save the ip_addr:port of the client's server
                if cmd in msg:
                    self._send_peer_list()                          # client wants a list of peers to connect to
        except socket.error:
            pass
        else:
            pass

    """ The list of the peers' servers for each client to connect to. """
    def _send_peer_list(self):
        self._socket.sendall(bytes(str(client), 'UTF-8'))

    def send_file(self, filename):
        self._socket.sendall(bytes(filename, 'UTF-8'))

    """ Override Thread.run() to send/receive messages through the socket. """
    def run(self, buff_size=2048):
        while True:
            if self._send() < 0:                                # send the TimeStamp
                self.exit()
                return
            self._receive()                                     # get a TimeStamp

    """ Close the connection and file. """
    def exit(self):
        self._socket.close()
        self._file.close()


def make_server(host='127.0.0.1', port=8080):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    print('Server started at\t' + host + '\nWaiting for client requests...')
    return server


def to_string(addr):
    return str(addr[0] + ':' + str(addr[1]))                    # 'ip_addr:port'


def run_server(server):
    while True:                                                 # make a new thread for each connected client
        server.listen(1)
        conn, addr = server.accept()                            # get the client's socket and address
        c = CThread(conn, to_string(addr))
        c.start()                                               # start the connection/thread with the client


if __name__ == '__main__':
    run_server(make_server())                                   # wait for clients to connect, saving their addresses

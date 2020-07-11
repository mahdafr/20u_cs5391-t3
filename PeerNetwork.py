import threading, socket, select, commands as cmd
from Server import CThread, to_string

host = '127.0.0.1'


class PeerNetwork(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)                             # create a new thread
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._host = (host, self._get_port())                       # the server's address
        self._peer = []
        self._sock = []

    """ Find a port to use for the listening socket. """
    def _get_port(self):
        self._server.bind((host, 0))                                # let the OS choose a port
        return self._server.getsockname()[1]

    """ Override Thread.run() to get connections. """
    def run(self):
        while True:                                                 # make a new thread for each connected client
            try:
                self._server.listen(1)                              # not limiting the number of connections
                conn, addr = self._server.accept()                  # get the client's socket and address
                addr = to_string(addr)
                self._peer.append(CThread(conn, addr))
                self._peer[-1].start()                              # start the connection/thread with the client
            except OSError:
                return

    def connect_to(self, peer_list):
        for p in peer_list:                                         # open a socket to each peer
            p = cmd.to_address(p)
            print('connected to', p)
            self._sock.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
            self._sock[-1].connect((p.split(cmd.split)))
            self._sock[-1].setblocking(0)

    """ Send the file to each peer. """
    def send_file(self, frm, filename):
        for p in self._sock:                                        # send file to those who this client connected to
            print(type(p))
            p.sendall(bytes(filename, 'UTF-8'))
            print('Sent file from:\t' + frm + 'to:\t' + p.socket.gethostbyname(socket.gethostname()))

    """ Get the address of the listener server. """
    def get_host(self):
        return self._host

    """ Close all the connected peers. """
    def exit(self):
        for p in self._peer:
            p.exit()
        self._server.close()
        print('Client at address\t' + str(self.get_host()) + '\tclosed their peer network.')

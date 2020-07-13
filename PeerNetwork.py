import threading, socket, commands as cmd

host = '127.0.0.1'


class PeerNetwork(threading.Thread):
    def __init__(self, id):
        threading.Thread.__init__(self)                             # create a new thread
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._host = (host, self._get_port())                       # the server's address
        self._peer = []
        self._sock = []
        self._id = id

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
                addr = cmd.to_string(addr)
                self._peer.append(PThread(conn, addr))
                self._peer[-1].start()                              # start the connection/thread with the client
            except OSError:
                return

    def connect_to(self, peer_list):
        if len(peer_list) == 1:                                     # create a new socket for one peer
            if cmd.is_same_addr(self.get_host(), peer_list[0]):     # do not open a connection to self
                print('Can\'t connect to self.')
                return
            self._connect_to(peer_list[0])
        else:
            for p in range(len(peer_list)):                         # open a socket to each peer
                if cmd.is_same_addr(self.get_host(), peer_list[p]): # do not open a connection to self
                    continue
                self._connect_to(peer_list[p])

    def _connect_to(self, p):
        self._sock.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        self._sock[-1].connect(p)
        self._sock[-1].setblocking(False)
        print('Client', self._id, 'connected to peer at', p)

    """ Send the file to each peer. """
    def send_file(self, filename):
        if self._sock is []:
            print('There are no peers to send files to.')
            return
        frm = 'Client ' + str(self._id)
        for p in self._sock:                                        # send file to every Peer
            to = p.getsockname()
            # p.setblocking(True)                                     # make sure the file goes through to end
            p.send(bytes(cmd.fstart, 'UTF-8'))
            with open(filename, 'rb') as f:                         # send line-by-line in bytes
                p.send(f.readline())
            p.send(bytes(cmd.fend, 'UTF-8'))
            print(frm, 'sent file to', to)

    """ Get the address of the listener server. """
    def get_host(self):
        return self._host

    """ Close all the connected peers. """
    def exit(self):
        for p in self._peer:
            p.exit()
        self._server.close()
        print('Client', self._id, 'closed their peer network.')


class PThread(threading.Thread):
    def __init__(self, c_sock, c_addr):
        threading.Thread.__init__(self)                         # create a new thread
        self._socket = c_sock
        self._addr = c_addr
        self._socket.setblocking(False)                         # non-blocking mode
        print('A Peer has connected at address:\t', self._addr)
        self._rec = []

    """ Send an ack for receipt of the File. """
    def _send(self, msg=cmd.fack):
        self._socket.sendall(bytes(msg, 'UTF-8'))

    """ Receive the file, without blocking the thread. """
    def _receive(self, buff_size=2048):
        try:                                                    # save what has been sent
            self._rec.append(self._socket.recv(buff_size).decode())
            if cmd.fstart in self._rec[-1]:
                print('Begin receiving a file...')
            if cmd.fend in self._rec[-1]:
                print('Received EOF.')
                self.exit()
        except socket.error:
            pass
        else:
            pass

    """ Override Thread.run() to send/receive messages through the socket. """
    def run(self, buff_size=2048):
        while True:
            self._receive()

    """ Close the connection. """
    def exit(self):
        self._socket.close()

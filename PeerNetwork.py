import threading, socket, commands as cmd


class PeerNetwork(threading.Thread):
    def __init__(self, id, filename):
        threading.Thread.__init__(self)                             # create a new thread
        self._listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listener_host = (cmd.host, self._get_port())          # the server's address
        self._peer_thread = []
        self._peers_connected_to = []
        self._peers = 0
        self._client_id = id
        self._me_str = 'Client ' + str(self._client_id)
        self._fname = filename

    """ Find a port to use for the listening socket. """
    def _get_port(self):
        self._listener.bind((cmd.host, 0))                          # let the OS choose a port
        return self._listener.getsockname()[1]

    """ Override Thread.run() to get connections. """
    def run(self):
        while True:                                                 # make a new thread for each connected client
            try:
                self._listener.listen(1)                            # not limiting the number of connections
                conn, addr = self._listener.accept()                # get the client's socket and address
                addr = cmd.to_string(addr)
                self._peer_thread.append(PThread(conn, addr, self._client_id, self._peers))
                self._peer_thread[-1].start()                       # start the connection/thread with the client
                self._peers+=1
            except OSError:
                return

    """ Connect to Peers' listener sockets and send the file, then close the connection. """
    def connect_and_send(self, peer_list):
        for p in range(len(peer_list)):                             # open a socket to each peer
            if cmd.is_same_addr(self.get_host(), peer_list[p]):     # do not open a connection to self
                continue
            conn = self._connect_to_peer(peer_list[p])
            self.send_file(self._fname, conn)
            conn.close()                                            # close the socket

    def _connect_to_peer(self, p):
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect(p)
        c.setblocking(False)
        print(self._me_str, 'connected to peer at', p)
        return c

    """ Send the file to each peer. """
    def send_file(self, filename, conn):
        to = conn.getsockname()
        # p.setblocking(True)                                   # make sure the file goes through to end
        conn.send(bytes(cmd.fstart, 'UTF-8'))
        with open(filename, 'rb') as f:                         # send line-by-line in bytes
            conn.send(f.readline())
        conn.send(bytes(cmd.fend, 'UTF-8'))
        print(self._me_str, 'sent file to', to)

    """ Get the address of the listener server. """
    def get_host(self):
        return self._listener_host

    def is_active(self):
        # did I send N files to my N Peers
        print(self._peers == len(self._peers_connected_to))
        return self._peers == len(self._peers_connected_to)

    """ Close all the connected peers. """
    def exit(self):
        for p in self._peer_thread:
            p.exit()
        self._listener.close()
        print(self._me_str, 'closed their peer network.')


class PThread(threading.Thread):
    def __init__(self, c_sock, c_addr, cid, id):
        threading.Thread.__init__(self)                             # create a new thread
        self._socket = c_sock
        self._addr = c_addr
        self._socket.setblocking(False)                             # non-blocking mode
        self._rec = []
        self._id = id
        self._client_id = cid
        self._me_str = 'Peer ' + str(self._id) + ' of Client ' + self._client_id

    """ Send an ack for receipt of the File. """
    def _send(self, msg=cmd.fack):
        self._socket.sendall(bytes(msg, 'UTF-8'))

    """ Receive the file, without blocking the thread. """
    def _receive(self, buff_size=2048):
        try:                                                        # save what has been sent
            self._rec.append(self._socket.recv(buff_size).decode())
            if cmd.fstart in self._rec[-1]:
                print(self._me_str + ' is receiving a file...')
            if cmd.fend in self._rec[-1]:
                print(self._me_str + ' received EOF.')
        except socket.error:
            pass

    """ Override Thread.run() to send/receive messages through the socket. """
    def run(self, buff_size=2048):
        while True:
            self._receive()

    """ Close the connection. """
    def exit(self):
        self._socket.close()

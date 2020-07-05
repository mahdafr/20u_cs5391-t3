import threading
import socket
from Server import CThread


class Peer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)                             # create a new thread
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._get_port()
        self._peer = []

    """ Find a port to use for the listening socket. """
    def _get_port(self, host='127.0.0.1'):
        for i in range(5000, 6000):
            try:
                self._server.bind((host, i))
                return
            except:
                print('Can\'t use port:\t', i)

    """ Override Thread.run() to get connections. """
    def run(self):
        while True:                                                 # make a new thread for each connected client
            try:
                self._server.listen(1)                              # not limiting the number of connections
                conn, addr = self._server.accept()                  # get the client's socket and address
                self._peer.append(CThread(conn, addr).start())      # start the connection/thread with the client
            except OSError:
                return

    """ Send the file to each peer. """
    def send_file(self, frm, filename):
        for p in self._peer:
            p.send_file(bytes(filename, 'UTF-8'))
            print('Sent file from:\t' + frm + 'to:\t' + p.get_address())

    """ Close all the connected peers. """
    def exit(self):
        for p in self._peer:
            p.exit()
        self._server.close()

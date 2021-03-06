import socket, threading, datetime
from TimeStamp import TimeStamp
from PeerNetwork import PeerNetwork
import commands as cmd

fname0 = 'out/client_'
fname1 = '_TimeData.txt'


class Client(threading.Thread):
    def __init__(self, id, host=cmd.host, port=cmd.port):
        threading.Thread.__init__(self)                         # create a new thread
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        self._socket.setblocking(False)                         # non-blocking mode
        self._host_ip = host
        self._my_ip = socket.gethostbyname(socket.gethostname())
        self._ts = TimeStamp(datetime.datetime.now())
        self._file = open(fname0+str(id)+fname1, 'a')           # append to this file
        self._peer = PeerNetwork(id, self._file.name)           # has a listener for peers
        self._id = id
        self._me_str = 'Client ' + str(self._id) + ' '

    """ Send a TimeStamp, if it is time to do so. """
    def _send(self):
        msg = self._ts.message(self._my_ip, self._host_ip, datetime.datetime.now())
        if msg is not None:
            self._socket.sendall(bytes(msg, 'UTF-8'))           # time to send the TimeStamp
            self._file.write(msg + '\n')                        # write to file

    """ Receive a TimeStamp, if it has been sent, without blocking the thread. """
    def _receive(self, buff_size=2048):
        try:
            msg = self._socket.recv(buff_size).decode()
            msg = cmd.clean(msg)
            self._file.write(msg + '\n')                        # write to file
        except ConnectionAbortedError:
            print('Server has closed the connection.')
            self.exit()
        except ConnectionResetError:
            print('Server has forcibly closed the connection.')
            self.exit()
        except BlockingIOError:
            # print('The connection is waiting for I/O operation.')
            pass

    """ Send the server this Client's listener address. """
    def _invite_peers(self):
        self._socket.sendall(bytes(cmd.s_cmd + str(self.get_server_address()), 'UTF-8'))
        print(self._me_str, 'has listener socket at address', self.get_server_address())

    """ Connect to Peers in the network, and send the files. """
    def _connect_to_peers(self):
        peer_list = self._get_peers()
        print(self._me_str + str(peer_list) + '\t' + str(len(peer_list)))
        connected = False
        while not connected:                                    # attempt the connection to the full peer list
            try:
                self._peer.connect_and_send(peer_list)
                connected = True
            except ConnectionRefusedError:
                continue

    """ Get the list of peers from the server in a readable format. """
    def _get_peers(self, buff_size=2048):
        self._socket.sendall(bytes(cmd.g_cmd, 'UTF-8'))
        pl = ''
        while pl == '':                                         # get the list of Peers' listener addresses
            try:
                msg = self._socket.recv(buff_size).decode()
                pl, ts = cmd.get_pl_and_ts(msg)
                if ts != '':
                    self._file.write(ts + '\n')                 # write the TimeStamp to file, if any
            except:
                continue
        return pl                                               # convert the list to (host, port) tuples

    """ Override Thread.run() to send/receive messages through the socket. """
    def run(self):
        self._peer.start()                                      # tell the server this Client's listener address
        self._invite_peers()
        while not self._ts.finished(datetime.datetime.now()):
            self._receive()                                     # get a TimeStamp; exit on error
            self._send()                                        # send the TimeStamp
        print(self._me_str + 'finished exchanging TimeStamps with the Server.')
        self._connect_to_peers()
        print(self._me_str + 'finished sending TimeStamp file to Peers.')
        # self.exit()

    """ Close the connection and file. """
    def exit(self):
        self._peer.exit()
        self._socket.close()
        self._file.close()
        print(self._me_str, 'disconnected at', datetime.datetime.now())

    def get_server_address(self):
        return self._peer.get_host()


if __name__ == '__main__':
    k = int(input('How many clients would you like to create?\t'))
    for i in range(k):
        Client(id=i).start()
        print('Client', i, 'created at', datetime.datetime.now())

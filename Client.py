import socket, threading, datetime
from TimeStamp import TimeStamp
from PeerNetwork import PeerNetwork

s_cmd = 'SERVERADDR'


class Client(threading.Thread):
    def __init__(self, filename, host='127.0.0.1', port=8080):
        threading.Thread.__init__(self)                         # create a new thread
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        self._socket.setblocking(0)                             # non-blocking mode
        self._host_ip = host
        self._my_ip = socket.gethostbyname(socket.gethostname())
        self._ts = TimeStamp(datetime.datetime.now())
        self._file = open(filename, 'a')                        # append to this file
        self._peer = PeerNetwork()                              # has a listener for peers

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
            self._file.write(msg + '\n')                        # write to file
        except ConnectionAbortedError:
            print('Server has closed the connection.')
            return -1
        except ConnectionResetError:
            print('Server has forcibly closed the connection.')
            return -1
        except BlockingIOError:
            return 0
        return 0

    """ Get the list of peers from the server. """
    def _build_network(self, cmd='GETPEERS', buff_size=2048):
        self._socket.sendall(bytes(cmd, 'UTF-8'))               # request the list
        self._peer.connect_to(list(self._socket.recv(buff_size).decode()))

    """ Override Thread.run() to send/receive messages through the socket. """
    def run(self):
        self._peer.start()
        self._socket.sendall(bytes(s_cmd + str(self._peer.get_host()), 'UTF-8'))
        while True:
            if self._receive() < 0:                             # get a TimeStamp
                self.exit()
                return
            self._send()                                        # send the TimeStamp
            if self._ts.finished(datetime.datetime.now()):      # should this client close the connection?
                self.exit()
                self._peer.send_file(self._my_ip, self._file.name)
                return

    """ Close the connection and file. """
    def exit(self):
        print('Client disconnected at\t' + str(datetime.datetime.now()))
        self._peer.exit()
        self._socket.close()
        self._file.close()

    def get_server_address(self):
        return self._peer.get_host()


if __name__ == '__main__':
    k = int(input('How many clients would you like to create?\t'))
    for i in range(k):
        Client(filename='out/client_' + str(i) + '_TimeData.txt').start()
        print('Client has been created at\t' + str(datetime.datetime.now()))

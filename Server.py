import socket, threading, datetime
from TimeStamp import TimeStamp
import commands as cmd

client_addr = []
client_thread = []


class CThread(threading.Thread):
    def __init__(self, c_sock, c_addr, file='out/serverTimeData.txt'):
        threading.Thread.__init__(self)                         # create a new thread
        self._socket = c_sock
        self._addr = c_addr
        self._socket.setblocking(False)                         # non-blocking mode
        print('A Client has connected at address:\t', self._addr)
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
                print('A Client has disconnected from:\t', self._addr)
                return -1
            except ConnectionResetError:
                print('A Client has forcibly disconnected from:\t', self._addr)
                return -1
        return 0

    """ Receive a TimeStamp, if it has been sent, without blocking the thread. """
    def _receive(self, buff_size=2048):
        try:
            msg = self._socket.recv(buff_size).decode()
            self._file.write(cmd.to_file(msg) + '\n')           # write the TimeStamp to file
            if cmd.got_server(msg):                             # save the ip_addr:port of the client's server
                client_addr.append(cmd.parse(msg))
                client_thread.append(self)
            if cmd.send_peers(msg):                             # send the list of peers for the client to connect
                self._socket.sendall(bytes(cmd.client_to_str(client_addr), 'UTF-8'))
        except socket.error:
            pass

    """ Override Thread.run() to send/receive messages through the socket. """
    def run(self, buff_size=2048):
        while True:
            if self._send() < 0:                                # keep sending TimeStamps?
                self.exit()
                return
            self._receive()                                     # get a TimeStamp

    """ Has this connection closed? """
    def test(self):
        try:
            self._socket.send(cmd.test)
        except:
            return True
        return False

    """ Close the connection and file. """
    def exit(self):
        self._socket.close()
        self._file.close()


def make_server(host=cmd.host, port=cmd.port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    print('Server started at\t' + host + '\nWaiting for client requests...')
    return server


def check_disconnects():
    if len(client_thread) == 0 or len(client_addr) == 0:
        return
    for i in range(len(client_thread)):                         # remove any closed connections for cleaner runs
        if client_thread[i].test():
            client_thread.pop(i)                                # remove the client's thread
            client_addr.pop(i)                                  # remove the listener's address


def run_server(server):
    while True:                                                 # make a new thread for each connected client
        server.listen(1)
        con, addr = server.accept()                             # get the client's socket and address
        c = CThread(con, cmd.to_string(addr))
        c.start()                                               # start the connection/thread with the client
        # check_disconnects()


if __name__ == '__main__':
    run_server(make_server())                                   # wait for clients to connect, saving their addresses

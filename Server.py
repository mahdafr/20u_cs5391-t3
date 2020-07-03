import socket
import threading
import datetime
from TimeStamp import TimeStamp


class CThread(threading.Thread):
    def __init__(self, c_sock, c_addr, file='out/serverTimeData.txt'):
        threading.Thread.__init__(self)                         # create a new thread
        self._socket = c_sock
        self._addr = c_addr
        print('Client has connected at address:\t', self._addr)
        self._ts = TimeStamp()
        self._file = open(file, 'a')

    def _send(self, now=datetime.datetime.now()):
        msg = self._ts.message(self._addr, socket.gethostbyname(socket.gethostname()), now)
        if msg is not None:
            self._socket.sendall(bytes(msg, 'UTF-8'))           # time to send the TimeStamp
            self._file.write(msg + '\n')                        # write to file

    def _receive(self, buff_size=2048):
        return self._socket.recv(buff_size).decode()

    def run(self, buff_size=2048):
        while True:
            self._send()                                        # send the data back

    def exit(self):
        print('Client at\t', self._addr, '\tdisconnected.')
        self._socket.close()


# open a stream to HOST, PORT and wait for clients to connect
if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 8080
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    print('Server started at\t' + HOST + '\nWaiting for client requests...')
    while True:                                                 # make a new thread for each connected client
        server.listen(1)
        conn, addr = server.accept()
        CThread(conn, addr).start()

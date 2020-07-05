import socket
import threading
import datetime
from TimeStamp import TimeStamp


class CThread(threading.Thread):
    def __init__(self, c_sock, c_addr, file='out/serverTimeData.txt'):
        threading.Thread.__init__(self)                         # create a new thread
        self._socket = c_sock
        self._addr = c_addr[0]
        self._socket.setblocking(0)                             # non-blocking mode
        print('Client has connected at address:\t', self._addr)
        self._ts = TimeStamp(datetime.datetime.now())
        self._file = open(file, 'a')

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

    def _receive(self, buff_size=2048):
        try:
            msg = self._socket.recv(buff_size).decode()
            self._file.write(msg + '\n')                        # write to file
        except socket.error:
            pass
        else:
            pass

    def run(self, buff_size=2048):
        while True:
            if self._send() < 0:                                # send the TimeStamp
                self.exit()
                return
            self._receive()                                     # get a TimeStamp

    def exit(self):
        self._socket.close()
        self._file.close()


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
        conn, addr = server.accept()                            # get the client's socket and address
        CThread(conn, addr).start()                             # start the connection/thread with the client

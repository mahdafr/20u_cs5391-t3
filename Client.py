import socket
import threading
import datetime
from TimeStamp import TimeStamp


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

    def _send(self):
        msg = self._ts.message(self._my_ip, self._host_ip, datetime.datetime.now())
        if msg is not None:
            self._socket.sendall(bytes(msg, 'UTF-8'))           # time to send the TimeStamp
            self._file.write(msg + '\n')                        # write to file

    def _receive(self, buff_size=2048):
        try:
            msg = self._socket.recv(buff_size).decode()
            self._file.write(msg + '\n')                        # write to file
        except socket.error:
            pass
        else:
            pass

    def run(self):
        while True:
            self._receive()                                     # send the TimeStamp
            self._send()                                        # get a TimeStamp
            if self._ts.finished(datetime.datetime.now()):      # should this client close the connection?
                self.exit()
                return

    def exit(self):
        print('Client disconnected at\t' + str(datetime.datetime.now()))
        self._socket.close()
        self._file.close()


if __name__ == '__main__':
    k = int(input('How many clients would you like to create?\t'))
    for i in range(k):
        Client(filename='out/client_' + str(i) + '_TimeData.txt').start()
        print('Client has been created at\t' + str(datetime.datetime.now()))

import socket
import datetime
import threading
from TimeStamp import TimeStamp


class Client(threading.Thread):
    def __init__(self, filename, host='127.0.0.1', port=8080):
        threading.Thread.__init__(self)                             # create a new thread
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))
        self._host_ip = host
        self._my_ip = socket.gethostbyname(socket.gethostname())
        self._file = open(filename, 'a')                            # append to this file
        self._ts = TimeStamp()

    def _send(self, now=datetime.datetime.now()):
        msg = self._ts.message(self._my_ip, self._host_ip, now)
        if msg is not None:
            self._socket.sendall(bytes(msg, 'UTF-8'))               # time to send the TimeStamp
            self._file.write(msg + '\n')                            # write to file

    def _receive(self, buff_size=2048):
        return self._socket.recv(buff_size).decode()

    def run(self):
        while True:
            self._send()
            if self._ts.finished():
                self.exit()

    def exit(self):
        print('Client will disconnect.')
        self._socket.close()
        self._file.close()


if __name__ == '__main__':
    k = int(input('How many clients would you like to create?\t'))
    for i in range(k):
        Client(filename='out/client_' + str(i) + '_TimeData.txt').start()

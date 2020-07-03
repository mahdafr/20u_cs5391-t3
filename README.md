# Assignment #3

In this assignment, you will be implementing socket programs for
1) a multi-threaded `Server`, and
2) a `Client` with peer-to-peer file transfer functionality.

The server should be able to take multiple requests at the same time.
The server is intended to provide Timestamp data to various clients.
Thus, the server's IP address and port number (5555) are availed to the clients who will connect to the server using TCP sockets.
The function of clients is to connect to the server and exchange their timestamp data with each other for 5 minutes.
After which, the clients will share their timestamp data file with each other.

_Note_: the server is __not__ involved in the file exchange process.

## Part I
The client will initiate the connection and send its Data/Time information to the server at every 10 milliseconds for a total of 5 minutes.
In return, the server also sends back its own Date/Time information to the client at the same rate.
Both server and clients must locally append these timestamp data to a file.
You can name the files as
- `serverTimeData.txt`, and
- `client_ID_TimeData.txt`.

These files must follow the format below:

_Timestamp Data_

| # | Sender's IP | Receiver's IP | Date  | Time  |
|---|-------------|---------------|-------|-------|
| 1 | Sender_IP   | Receiver_IP   | Date0 | Time0 |
| 2 | Sender_IP   | Receiver_IP   | Date1 | Time1 |
| 3 | Sender_IP   | Receiver_IP   | Date2 | Time2 |
| 4 | ...         | ...           | ...   | ...   |

_End of Timestamp Data (after 5 minutes)_

- To get the current time, I used the `datetime` library.
    - [this StackOverflow page](https://stackoverflow.com/questions/1345827/how-do-i-find-the-time-difference-between-two-datetime-objects-in-python) provided several examples on functions to check time elapsed
    - there are 1000 microseconds in a millisecond (so, 10ms is 10000 microseconds)
    - there are 60s in a minute (so, 5m is 300s)
    - these times helped each client thread to know when to store a timestamp and when to kill their threads

## Part II
While one client is already communicating with the server, you will run two other client programs that do the same tasks as described above.
Make sure they have unique files that store the timestamp data.

## Part III
In this part, the clients are required to exchange their timestamp data files with each other in a peer-to-peer fashion.
I encourage to think on how generically you can develop a program, which will allow _k_ Clients/Peers to efficiently share their timestamp data files with each other.

## References
http://net-informations.com/python/net/thread.htm

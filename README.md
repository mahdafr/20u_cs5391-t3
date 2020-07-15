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

### Results
- To get the current time, I used the `datetime` library.
    - [this StackOverflow page](https://stackoverflow.com/questions/1345827/how-do-i-find-the-time-difference-between-two-datetime-objects-in-python) provided several examples on functions to check time elapsed
    - there are 1000 microseconds in a millisecond (so, 10ms is 10000 microseconds)
    - there are 60s in a minute (so, 5m is 300s)
    - these times helped each client thread to know when to store a timestamp and when to close their connections (killing threads); see Part 3 for their last actions
- In order to prevent race conditions in the socket connections, I used the `socket.setblocking(FLAG)` method
    - the `FLAG` parameter is set to `False` in order to prevent waiting
    - this is similar to the `settimeout()` method of the Python [socket](https://docs.python.org/3/library/socket.html) library

## Part II
While one client is already communicating with the server, you will run two other client programs that do the same tasks as described above.
Make sure they have unique files that store the timestamp data.

### Results
- The program asks the user for how many clients to create on the system.
    - For each client made, there is a file created to output the sent/received TimeStamps
    - Clients' IDs starting from `0` to _`k`_, where _k_ is the user's input for the number of Clients
    - Files will be stored in an `out` directory of the project (not included in the repo; see [.gitignore](https://github.com/mahdafr/20u_cs5391-t3/blob/master/.gitignore) file)

## Part III
In this part, the clients are required to exchange their timestamp data files with each other in a peer-to-peer fashion.
I encourage to think on how generically you can develop a program, which will allow _k_ Clients/Peers to efficiently share their timestamp data files with each other.

### Results
- Each client is a server (see [this StackOverflow question](https://stackoverflow.com/questions/23267305/python-sockets-peer-to-peer))
    - where the listening socket picks a port (from 5000:6000) on the localhost (_therefore, my program can only handle at most 1001 clients_)
    - where the connections are made through the main server (from Part 1) who stores the list of connected clients' listening server addresses
    - the list of sockets are stored and the list of clients' (peers who connected through the listener server) are also stored, see [this StackOverflow question](https://stackoverflow.com/questions/17539859/how-to-create-multi-server-sockets-on-one-client-in-python) which uses the Python [select](https://docs.python.org/2/library/select.html) library
- Once a client's lifecycle completes (at 5m):
    - the Client requests the list of peers from the Server
    - the Client send iterates through the list of peers
        - it connects to each Peer (_here, many issues occurred when debugging multithreaded output and parsing the list of Peers' addresses correctly_)
        - it sends its TimeStamp file to each of its Peers (_the file is opened as read-only, as bytes, and read in a single call: `f.read()`_)
        - it closes the connection (_connections (via sockets) can be saved, though are not for the purposes of this assignment_)
        - since the list will have all the addresses of the Clients' listener sockets, a Client will not connect to itself
    - each connected peer will receive a file from a client
        - Peers receive a `FILESTART` command from their Peers to signal the file about to be sent and `FILEEND` to acknowledge receipt
        - Peers save each message received
        - Peers do not save received data to files, though this can be feasibly changed
- Some TODOs remain, for improved program usability
    - keep track of Server's Clients (and remove from saved list of Clients) to avoid restarting program for new tests
    - close Client (and their PeerNetwork) when they finish sending/receiving files from all Peers

## To Run
1. Create an `out/` directory in the same folder as this project to output files.
2. Run the `Server.py` script first. _Note_: Server will continually update its file with sent TimeStamps throughout the life of the program.
3. Run the `Client.py` script second. Enter the number of clients to create.
4. End the executables when all Clients have completed their Task.

## References
http://net-informations.com/python/net/thread.htm

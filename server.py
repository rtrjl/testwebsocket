import asyncio
import socket
import signal
import os


loop = asyncio.get_event_loop()

bquit = b'QUIT\r\n'

def signal_handler():
    print ('\nCTRL+C pressed, exiting...\n')
    print ("pid %s: send SIGINT to exit." % os.getpid())
    loop.stop()


@asyncio.coroutine
def handle_client(client, addr):
    print ("Client connected : {}".format(addr))
    while True:
        data = yield from loop.sock_recv(client, 4096)
        if not data:
            print("Client has disconnected")
            break
        
        if data == bquit  :
            client.close()
            break

        client.send("Tu m'as envoyé:".encode() + data)


@asyncio.coroutine
def accept_connections(server_socket):
    while True:
        client, addr = yield from loop.sock_accept(server_socket)
        asyncio.async(handle_client(client, addr))



server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
server.bind(('127.0.0.1', 1234))
server.listen(128)
server.setblocking(False)
print("Server listening on {}".format(server.getsockname()))
print("Pid is : %s" % os.getpid())
print("Ctrl + C to exit")

loop.add_signal_handler(signal.SIGINT, signal_handler)

try:
    loop.run_until_complete(accept_connections(server))
except Exception as e:
    print("Exception :%s "% e)



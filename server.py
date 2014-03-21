import asyncio
import socket

loop = asyncio.get_event_loop()


@asyncio.coroutine
def handle_client(client, addr):
    print ("Client connected : {}".format(addr))
    while True:
        data = yield from loop.sock_recv(client, 4096)
        if not data:
            print("Client has disconnected")
            break
        client.send("tu m'as envoyé:".encode() + data)


@asyncio.coroutine
def accept_connections(server_socket):
    while True:
        client, addr = yield from loop.sock_accept(server_socket)
        asyncio.async(handle_client(client, addr))



server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
server.bind(('127.0.0.1', 1234))
server.listen(128)
server.setblocking(False)
print ("Server listening on {}".format(server.getsockname()))


loop.run_until_complete(accept_connections(server))



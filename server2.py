import asyncio
import websocket


incomingQueue = asyncio.Queue()
outgoingQueue = asyncio.Queue()
banned = dict()


class PicoChatProtocol(asyncio.Protocol):
    def __init__(self, ):
        self.handshake_done = False

    def connection_made(self, transport):
        self.transport = transport
        self.transport.max_size = 2048
        if transport.get_extra_info('peername')[0] in banned:
            self.transport.close()
        peername = transport.get_extra_info('peername')
        print('connection from {}'.format(peername))

    def data_received(self, data):
        # len(data) < 1024 < self.transport.max_size
        if len(data) > 1024:
            banned[self.transport.get_extra_info('peername')[0]] = True
            self.transport.close()
            return 0

        if self.handshake_done is False:
            request = websocket.WebSocketHTTPRequest(data)
            response = request.handshake()
            self.transport.write(response)
            self.handshake_done = True
        else:
            frame = websocket.WSIncomingFrame(data)
            incomingQueue.put(frame)
            response = websocket.WSOutGoingFrame("response".encode())
            self.transport.write(response.bytes_frame)


loop = asyncio.get_event_loop()
coro = loop.create_server(PicoChatProtocol, '127.0.0.1', 9999)
server = loop.run_until_complete(coro)
print('serving on {}'.format(server.sockets[0].getsockname()))

try:
    loop.run_forever()
except KeyboardInterrupt:
    print("exit")
finally:
    server.close()
    loop.close()

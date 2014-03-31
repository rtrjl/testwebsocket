import asyncio
from http.server import BaseHTTPRequestHandler
from io import StringIO


incomingQueue = asyncio.Queue()


class WebSocketRequest():
    MAXHEADERS = 4096

    def __init__(self, request_data):
       
        self.parse_request(request_data)
    
    def handshake(self):
        #wskey = self.headers.get('Sec-WebSocket-Key')
        print("coucou")
        
    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

    def parse_request(self, request_data):
        headers = {}
        if len(request_data) > 4096:
            raise HTTPException("Header request too long")
        request_str = request_data.decode()
        #for line in request_str


class PicoChatProtocol(asyncio.Protocol):
    def __init__(self):
        self.handshake_done = False

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        if self.handshake_done is False:
            req = WebSocketRequest(data)
            req.handshake()
            self.transport.write(data)

        # close the socket
        self.transport.close()

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







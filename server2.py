import asyncio
from http.server import BaseHTTPRequestHandler
from StringIO import StringIO


incomingQueue = asyncio.Queue()


class WebSocketRequest(BaseHTTPRequestHandler):

    def __init__(self, request_data):
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()
    
    def handshake(self):
        return 1
        

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message


class PicoChatProtocol(asyncio.Protocol):
    def __init__(self):
        self.handshake_done = False

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        print(data.decode())
        if self.handshake_done is False:
            
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


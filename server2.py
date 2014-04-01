import asyncio
import base64
from hashlib import sha1
from io import StringIO


incomingQueue = asyncio.Queue()


class WSException(Exception):
    # Subclasses that define an __init__ must call Exception.__init__
    # or define self.args.  Otherwise, str() will fail.
    pass


class WebSocketRequest():
    MAX_HEADERS = 4096
    WS_MAGIC_KEY = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    http_method = ""
    http_version = ""
    http_path = ""
    headers = {}

    def __init__(self, request_data):
        self.parse_request(request_data)

    def handshake(self):
        ws_key = ""
        ws_version = 0
        try:
            ws_key = self.headers['Sec-WebSocket-Key']
        except KeyError:
            raise WSException("WebSocket key missing")
        #ws_key = 
        #ws_key = ws_key.decode()
        if len(base64.b64decode(ws_key)) != 16:
            raise WSException("Websocket key lenght is != 16")
        try:
            ws_version = int(self.headers['Sec-WebSocket-Version'])
        except ValueError:
            raise WSException("Websocket version must be an integer")
        if ws_version != 13:
            raise WSException("Websocket version must be 13")

        handshake_headers = {
            'Upgrade': "websocket",
            'Connection': "Upgrade",
        }
        print(type(self.WS_MAGIC_KEY))
        ws_accept_key = base64.b64encode(sha1(ws_key.encode('utf-8')
                                              + self.WS_MAGIC_KEY.encode('utf-8')).digest())
        handshake_headers['Sec-WebSocket-Accept'] = ws_accept_key
        response = "HTTP/1.1 101 Switching Protocols\r\n"

        for key in handshake_headers.keys():
            response += str(key) + ": " + handshake_headers[key]+"\r\n"

        return response.encode()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

    def parse_request(self, request_data):
        if len(request_data) > self.MAX_HEADERS:
            raise WSException("Request too long for me")

        request_str = StringIO(request_data.decode())
        try:
            self.http_method, self.http_path, self.http_version \
                = request_str.readline().split(" ")
        except:
            raise WSException("Malformed request line")

        if self.http_method != "GET":
            raise WSException("HTTP method must be GET")

        for line in request_str.readlines():
            if line in ("\r\n", "\n", ""):
                break
            key, value = line.split(":", 1)
            self.headers[key] = value.strip()


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
            rep = req.handshake()
            print(rep
)
            self.transport.write(rep)

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

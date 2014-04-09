import asyncio
import base64
import struct
from hashlib import sha1
from io import StringIO, BytesIO


incomingQueue = asyncio.Queue()



class WSClient():

    def __init__(self, transport):
        self.transport = transport


class WSException(Exception):
    # Subclasses that define an __init__ must call Exception.__init__
    # or define self.args.  Otherwise, str() will fail.
    pass


class WebSocketFraming():
    OP_CONTINUATION = 0
    OP_TEXT = 1
    OP_BINARY = 2
    OP_CLOSE = 8
    OP_PING = 9
    OP_PONG = 10


    fin = False
    opcode = 0
    data = 0
    payload_length = 0
    masking_key = 0





    def __init__(self, frame_bytes):
        self.parse_bytes(frame_bytes)

    def parse_bytes(self, frame_bytes):
        bio = BytesIO(frame_bytes)
        databuffer = bio.getbuffer()
        self.fin = bool(databuffer[0] & 0b10000000)
        self.opcode = databuffer[0] & 0b00001111
        masked = bool(databuffer[1] & 0b10000000)
        self.payload_length = databuffer[1] & 0b01111111
        index = 2
        if self.payload_length == 126:
            self.payload_length = struct.unpack(">H", bytes(databuffer[2:4]))[0]
            index += 3
        if self.payload_length == 127:
            self.payload_length = struct.unpack(">Q", bytes(databuffer[2:10]))[0]
            index += 9
        if masked:
            self.masking_key = struct.unpack("I", bytes(databuffer[index:index+4]))[0]
            index += 3
        print(self.masking_key)




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

        if len(base64.b64decode(ws_key)) != 16:
            raise WSException("Websocket key length is != 16")

        try:
            ws_version = int(self.headers['Sec-WebSocket-Version'])
        except ValueError:
            raise WSException("Websocket version must be an integer")

        if ws_version != 13:
            raise WSException("Websocket version must be 13")

        handshake_headers = {'Upgrade': "websocket", 'Connection': "Upgrade",
                             'Sec-WebSocket-Accept': base64.b64encode(sha1(ws_key.encode('utf-8')
                                                                           + self.WS_MAGIC_KEY.encode(
                                 'utf-8')).digest()).decode('utf-8')}

        response = "HTTP/1.1 101 Switching Protocols\r\n"
        for key in handshake_headers.keys():
            response += str(key) + ": " + handshake_headers[key]+"\r\n"
        response += "\r\n"
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
            request = WebSocketRequest(data)
            response = request.handshake()
            self.transport.write(response)
            self.handshake_done = True
        else:
            frame = WebSocketFraming(data)


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

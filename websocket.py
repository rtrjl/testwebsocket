from hashlib import sha1
import base64
from io import StringIO
import struct


class WSClient():
    def __init__(self, transport):
        self.transport = transport


class WSException(Exception):
    # Subclasses that define an __init__ must call Exception.__init__
    # or define self.args.  Otherwise, str() will fail.
    pass

class WebSocketHTTPRequest():
    MAX_HEADERS = 1024
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
            response += str(key) + ": " + handshake_headers[key] + "\r\n"
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


class WSIncomingFrame():
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
        self.fin = bool(frame_bytes[0] & 0b10000000)
        self.opcode = frame_bytes[0] & 0b00001111
        masked = bool(frame_bytes[1] & 0b10000000)
        self.payload_length = frame_bytes[1] & 0b01111111
        index = 2
        if self.payload_length == 126:
            self.payload_length = struct.unpack(">H", bytes(frame_bytes[2:4]))[0]
            index += 2
        if self.payload_length == 127:
            self.payload_length = struct.unpack(">Q", bytes(frame_bytes[2:10]))[0]
            index += 8
        if masked:
            self.masking_key = bytes(frame_bytes[index:index + 4])
            index += 4

        self.data = bytes(frame_bytes[index:index + self.payload_length])
        decoded_data = list()
        for i, value in enumerate(self.data):
            decoded_data.append(value ^ self.masking_key[i % 4])
        self.data = bytes(decoded_data)


class WSOutGoingFrame():
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
    bytes_frame = None

    def __init__(self, data):
        self.build_frame(data)

    def build_frame(self, data):
        length = len(data)
        response = list()
        response.append(0b10000001)
        if length <= 126:
            response.append(length)
        if 126 <= length <= 65535:
            response.append(126)
            response.extend(struct.pack(">H", length))
        if length >= 65535:
            response.append(127)
            response.extend(struct.pack(">Q", length))
        response.extend(data)
        self.bytes_frame = bytes(response)

import struct
import os

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
            x = struct.pack(">H", length)
            response.extend([x[0], x[1]])
        if length >= 65535:
            response.append(127)
            x = struct.pack(">Q", length)
            response.extend([x[0], x[1], x[2], x[3]])
        for octet in data:
            response.append(octet)
        self.bytes_frame = bytes(response)

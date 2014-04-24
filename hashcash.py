import os
import struct
import hashlib

a = "hello this is a msg"

b = struct.unpack("I", os.urandom(4))[0]

turn = 0

byte_test_table = [127, 63, 31, 15, 7, 3, 1, 0]


def test_byte(bytetotest, nb_bits):
    if ( bytetotest > byte_test_table[nb_bits-1]):
        return False
    else:
        return True

def test_bytes(bytestotest, nb_bits):
    reste = nb_bits % 8
    if reste != 0:
        nb_bytes = (nb_bits // 8) + 1
    else:
        nb_bytes = nb_bits //8
    nb_bits = reste

    for i in range(nb_bytes):
        if nb_bytes-1 > i:
            if test_byte(bytestotest[i], 8):
                continue
            else:
                return False

    return test_byte(bytestotest[i], nb_bits)




while True:
    turn = turn+1
    b = b + turn
    msg=a+"::"+str(b)
    hash = hashlib.sha256(msg.encode()).hexdigest()
    hash2 = hashlib.sha256(msg.encode()).digest()
    if test_bytes(hash2, 19):
        print(msg)
        print(hash)
        for octet in hash2:
            print(octet)
        break
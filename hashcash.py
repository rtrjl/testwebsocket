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
    nb_bytes = nb_bits / 8
    nb_bits = nb_bits % 8

    for i in range(nb_bytes):
        if nb_bits != 0:
            
        if bytestotest[i] == 0 and (i+1) == nb_bytes :
            if nb_bits !=0:




while True:
    turn = turn+1
    b = b + turn
    msg=a+"::"+str(b)
    hash = hashlib.sha1(msg.encode()).hexdigest()
    hash2 = hashlib.sha1(msg.encode()).digest()
    print(len(hash2))
    if test_byte(hash2[0], 8):
        print(hash)
        break
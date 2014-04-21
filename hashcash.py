import os
import struct
import hashlib
a = "hello this is a msg"
b = struct.unpack("I", os.urandom(4))[0]
turn = 0
while True:
    turn = turn+1
    b = b + turn
    msg=a+"::"+str(b)
    hash = hashlib.sha1(msg.encode()).hexdigest()
    if hash[0:5] == "00000":
        print(hash)
        print(b)
        print(turn)
        break
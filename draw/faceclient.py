import socket
import struct

VERSION = 0x1000
PACKET_VALID = 1
PACKET_INVALID = 0

fn = "/tmp/facetracker"

if __name__ == "__main__":
    so = socket.socket(
        family=socket.AF_UNIX,
        type=socket.SOCK_STREAM
    )
    try:
        so.connect(fn)
        while True:
            version, packettype = struct.unpack('!II', so.recv(4 * 2))
            if packettype == PACKET_INVALID:
                print("invalid")
            elif packettype == PACKET_VALID:
                t, x, y, z = struct.unpack('!dfff', so.recv(8 + 4*3))
                print(t, x, y, z)
    finally:
        so.close()

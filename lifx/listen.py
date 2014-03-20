
from pprint import pprint
import socket
from . import packetcodec
from binascii import hexlify

def main():
    UDP_IP = "0.0.0.0"
    UDP_PORT = 56700
    
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_DGRAM)
    
    sock.bind((UDP_IP, UDP_PORT))
    
    while True:
        data, addr = sock.recvfrom(1024)
        packet = packetcodec.decode_packet(data)
        print(addr, unicode(packet))
        pprint(packet.payload.data)

if __name__ == '__main__':
    main()


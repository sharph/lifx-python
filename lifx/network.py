

import socket
import struct
from binascii import hexlify
from time import time

from . import packetcodec

IP = '0.0.0.0'
BCAST = '255.255.255.255'
PORT = 56700

targetaddr = None
connection = None
debug = False
site = b'\00\00\00\00\00\00'

def connect():
    global connection, site, targetaddr
    udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udpsock.bind((IP, PORT))
    p = packetcodec.Packet(packetcodec.GetPANGatewayPayload())
    for x in range(5):
        udpsock.sendto(p.__bytes__(), (BCAST, PORT))
    while True:
        data, addr = udpsock.recvfrom(1024)
        packet = packetcodec.decode_packet(data)
        if packet is not None and \
                isinstance(packet.payload, packetcodec.PANGatewayPayload):
            break
    #udpsock.close()
    if debug:
        print( 'found light: %s' % (addr[0], ))
    #tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #tcpsock.settimeout(2.0)
    #tcpsock.connect(addr)
    #connection = tcpsock
    targetaddr = addr
    udpsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 0)
    udpsock.settimeout(0.1)
    connection = udpsock
    site = packet.site
    if debug:
        print( 'connection established with %s' % (unicode(hexlify(site),
                                                      encoding='utf-8')))

def sendpacket(p):
    global connection, site, targetaddr
    if connection is None:
        connect()
    p.site = site
    if debug:
        print('sendpacket:  ', p)
        print('IP:  ', targetaddr[0])
        print('Port:  ', targetaddr[1])
    #connection.sendall(bytes(p))
    connection.sendto(bytes(p), targetaddr)

def recvpacket(timeout = None):
    global connection
    if connection is None:
        connect()
    #connection.settimeout(timeout)
    #try:
    #    lengthdatum, addr = connection.recvfrom(2)
    #except socket.timeout:
    #    return None
    #connection.settimeout(None)
    #try:
    #    (length, ) = struct.unpack('<H', lengthdatum)
    #except struct.error:
    #    connect()
    #    return None
    #data, addr = connection.recvfrom(length - 2)
    try:
        data, addr = connection.recvfrom(1024)
    except socket.timeout:
        return None
    packet = packetcodec.decode_packet(data)
    if debug:
        print('recvpacket(): ', packet)
    return packet

def listenforpackets(seconds, desired = None, target = None):
    start = time()
    packets = []
    if debug:
        print('listenforpackets() Start: ', start)
    while time() - start < seconds:
        p = recvpacket(0.1)
        if p is not None:
            packets.append(p)
            if desired is not None and isinstance(p.payload, desired):
                if target is not None and p.target != target:
                    continue
                return packets
    return packets


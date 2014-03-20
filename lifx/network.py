#!/usr/bin/python3

import socket
import struct
from binascii import hexlify
from time import time, sleep

from . import packetcodec

IP = '0.0.0.0'
BCAST = '255.255.255.255'
PORT = 56700

connection = None
debug = False
site = b'\00\00\00\00\00\00'

def connect():
    global connection, site
    udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udpsock.bind((IP, PORT))
    p = packetcodec.Packet(packetcodec.GetPANGatewayPayload())
    for x in range(5):
        udpsock.sendto(bytes(p), (BCAST, PORT))
    for x in range(10):
        try:
            udpsock.settimeout(0.2)
            data, addr = udpsock.recvfrom(1024)
            packet = packetcodec.decode_packet(data)
            if packet is not None and \
                    isinstance(packet.payload, packetcodec.PANGatewayPayload):
                break
        except socket.timeout:
            pass
    udpsock.close()
    if not isinstance(packet.payload, packetcodec.PANGatewayPayload):
        connection = None
        return
    if debug:
        print('found light: %s' % (addr[0], ))
    tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpsock.settimeout(2.0)
    tcpsock.connect(addr)
    connection = tcpsock
    site = packet.site
    if debug:
        print('connection established with %s' % (str(hexlify(site),
                                                      encoding='utf-8')))

def sendpacket(p):
    global connection, site
    if connection is None:
        connect()
    if connection is None:
        if debug:
            print(p)
            print("Packet not sent!")
        return
    p.site = site
    if debug:
        print(p)
    connection.sendall(bytes(p))

def recvpacket(timeout = None):
    global connection
    if connection is None:
        connect()
    if connection is None:
        return None
    connection.settimeout(timeout)
    try:
        lengthdatum, addr = connection.recvfrom(2)
    except socket.timeout:
        return None
    connection.settimeout(None)
    try:
        (length, ) = struct.unpack('<H', lengthdatum)
    except struct.error:
        connect()
        return None
    data, addr = connection.recvfrom(length - 2)
    packet = packetcodec.decode_packet(lengthdatum + data)
    if debug:
        print(packet)
    return packet

def listenforpackets(seconds, desired = None, target = None):
    start = time()
    packets = []
    while time() - start < seconds:
        p = recvpacket(0.1)
        if p is not None:
            packets.append(p)
            if desired is not None and isinstance(p.payload, desired):
                if target is not None and p.target != target:
                    continue
                return packets
    return packets


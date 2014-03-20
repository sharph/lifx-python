
from . import network
from . import packetcodec
import socket
from time import clock
from binascii import hexlify, unhexlify
import struct

lights = {}

def inttohex(n):
    return str(hexlify(struct.pack('>H', n)), encoding='utf-8')

class LIFXBulb:
    def __init__(self, lightstatus):
        self.recv_lightstatus(lightstatus)

    def __repr__(self):
        return "<LIFXBulb %s hue:%s sat:%s bright:%s kelvin:%s on:%s>" % \
               (self.get_addr(),
                inttohex(self.hue),
                inttohex(self.saturation),
                inttohex(self.brightness),
                self.kelvin,
                self.power)

    def get_addr(self):
        return str(hexlify(self.addr), encoding='utf-8')

    def deliverpacket(self, packet):
        if isinstance(packet.payload, packetcodec.LightStatusPayload):
            self.recv_lightstatus(packet)
        elif isinstance(packet.payload, packetcodec.PowerStatePayload):
            self.recv_powerstate(packet)

    def recv_lightstatus(self, lightstatus):
        self.addr = lightstatus.target
        self.hue = lightstatus.payload.data['hue']
        self.saturation = lightstatus.payload.data['saturation']
        self.brightness = lightstatus.payload.data['brightness']
        self.kelvin = lightstatus.payload.data['kelvin']
        self.dim = lightstatus.payload.data['dim']
        if lightstatus.payload.data['power'] > 0:
            self.power = True
        else:
            self.power = False
        self.bulb_label = str(lightstatus.payload.data['bulb_label'],
                              encoding='utf-8').strip('\00')
        self.tags = lightstatus.payload.data['tags']

    def recv_powerstate(self, powerstate):
        if powerstate.payload.data['onoff'] > 0:
            self.power = True
        else:
            self.power = False

    def get_state(self):
        clear_buffer()
        p = packetcodec.Packet(packetcodec.GetLightStatePayload())
        p.target = self.addr
        network.sendpacket(p)
        listen_and_interpret(5, packetcodec.LightStatusPayload, self.addr)

    def set_power(self, power):
        set_power(self.addr, power)
        listen_and_interpret(5, packetcodec.PowerStatePayload, self.addr)

    def set_color(self, hue, saturation, brightness, kelvin, fade_time):
        set_color(self.addr, hue, saturation, brightness, kelvin, fade_time)

def sanitize_addr(addr):
    if len(addr) > 6:
        return unhexlify(bytes(addr, encoding='utf-8'))
    return addr

def set_color(addr, hue, saturation, brightness, kelvin, fade_time):
    addr = sanitize_addr(addr)
    clear_buffer()
    p = packetcodec.Packet(packetcodec.SetLightColorPayload())
    p.payload.data['hue'] = hue
    p.payload.data['saturation'] = saturation
    p.payload.data['brightness'] = brightness
    p.payload.data['kelvin'] = kelvin
    p.payload.data['fade_time'] = fade_time
    p.target = addr
    network.sendpacket(p)
    clear_buffer()

def set_power(addr, power):
    addr = sanitize_addr(addr)
    clear_buffer()
    p = packetcodec.Packet(packetcodec.SetPowerStatePayload())
    p.target = addr
    if power:
        p.payload.data['onoff'] = 0x0001
    else:
        p.payload.data['onoff'] = 0x0000
    network.sendpacket(p)

def pause(sec):
    listen_and_interpret(sec)

def listen_and_interpret(sec, desired = None, target = None):
    global lights
    packets = network.listenforpackets(sec, desired, target)
    for p in packets:
        if p.target not in lights:
            if isinstance(p.payload, packetcodec.LightStatusPayload):
                lights[p.target] = LIFXBulb(p)
        else:
            lights[p.target].deliverpacket(p)

def get_lights():
    global lights
    p = packetcodec.Packet(packetcodec.GetLightStatePayload())
    for x in range(4):
        network.sendpacket(p)
        listen_and_interpret(0.5)
    return list(lights.values())

def clear_buffer():
    listen_and_interpret(0.05)

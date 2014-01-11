
from struct import pack, unpack, calcsize
from binascii import hexlify as tohex

from .lifxconstants import *

class Packet:
    def __init__(self, payload = None):
        self.size = 0
        self.proto = 0x3400
        self.target = b'\00\00\00\00\00\00'
        self.site = b'\00\00\00\00\00\00'
        self.timestamp = 0
        if payload is None:
            self.payload = LIFXPayload()
        else:
            self.payload = payload

    def __str__(self):
        return('<packet proto:%s, target:%s, site:%s, type:%s>' %
               (str(tohex(pack('>H', self.proto)), encoding='utf-8'),
                str(tohex(self.target), encoding='utf-8'),
                str(tohex(self.site), encoding='utf-8'),
                self.payload.name ))

    def __bytes__(self):
        encoded_payload = self.payload.encode()
        self.size = 36 + len(encoded_payload)
        header = pack('<HHI6sH6sHQHH',
                      self.size,
                      self.proto,
                      0x0000,
                      self.target,
                      0x0000,
                      self.site,
                      0x0000,
                      self.timestamp,
                      self.payload.packet_type,
                      0x0000)
        return header + encoded_payload
        

class LIFXPayload:
    packet_type = 0
    pack_str = '<'
    pack_struct = []
    name = 'LIFX'
    
    def __init__(self, data = None):
        self.data = dict([ (datum_name, 0x00) for datum_name in self.
                           pack_struct ])
        if data is not None:
            self.decode(data)

    def encode(self):
        ordered_data = [self.data[datum_name] for datum_name in
                        self.pack_struct]
        return pack(self.pack_str, *ordered_data)

    def decode(self, bs):
        if len(bs) != calcsize(self.pack_str):
            print('could not decode %s' % (self.name, ))
            print(tohex(bs))
            return
        data = unpack(self.pack_str, bs)
        self.data = dict( zip(self.pack_struct, data) )

    def __bytes__(self):
        return self.encode()

class GetPANGatewayPayload(LIFXPayload):
    name = 'Get PAN Gateway'
    packet_type = GET_PAN_GATEWAY

class PANGatewayPayload(LIFXPayload):
    name = 'PAN Gateway'
    packet_type = PAN_GATEWAY
    pack_str = '<BI'
    pack_struct = ['service', 'port']

class GetLightStatePayload(LIFXPayload):
    name = 'Get light state'
    packet_type = GET_LIGHT_STATE

class SetLightColorPayload(LIFXPayload):
    name = 'Set light color'
    packet_type = SET_LIGHT_COLOR
    pack_str = '<BHHHHI'
    pack_struct = ['stream',
                   'hue',
                   'saturation',
                   'brightness',
                   'kelvin',
                   'fade_time']

class LightStatusPayload(LIFXPayload):
    name = 'Light status'
    packet_type = LIGHT_STATUS
    pack_str = '<HHHHHH32sQ'
    pack_struct = ['hue',
                   'saturation',
                   'brightness',
                   'kelvin',
                   'dim',
                   'power',
                   'bulb_label',
                   'tags']

class GetPowerStatePayload(LIFXPayload):
    name = 'Get power state'
    packet_type = GET_POWER_STATE

class SetPowerStatePayload(LIFXPayload):
    name = 'Set power state'
    packet_type = SET_POWER_STATE
    pack_str = '<H'
    pack_struct = ['onoff']

class PowerStatePayload(SetPowerStatePayload):
    name = 'Power state'
    packet_type = POWER_STATE

    
def decode_packet(data):
    mapping = {GET_PAN_GATEWAY: GetPANGatewayPayload,
               PAN_GATEWAY: PANGatewayPayload,
               GET_LIGHT_STATE: GetLightStatePayload,
               SET_LIGHT_COLOR: SetLightColorPayload,
               LIGHT_STATUS: LightStatusPayload,
               GET_POWER_STATE: GetPowerStatePayload,
               SET_POWER_STATE: GetPowerStatePayload,
               POWER_STATE: PowerStatePayload}
    if len(data) < 36:
        return None
    p = Packet()
    data, payload = unpack('<HHI6sH6sHQHH', data[:36]), data[36:]
    p.size = data[0]
    p.proto = data[1]
    p.target = data[3]
    p.site = data[5]
    p.timestamp = data[7]
    packet_type = data[8]
    if packet_type in mapping:
        p.payload = mapping[packet_type](payload)
    else:
        p.payload = LIFXPayload()
    return p

def encodepacket(p):
    pass


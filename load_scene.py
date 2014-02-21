#!/usr/bin/env python3

import sys

from binascii import unhexlify
from struct import unpack

import lifx

def fromhex(datum):
    return unhexlify(bytes(datum, encoding='utf-8'))

def intfromhex(datum):
    return unpack('>H',fromhex(datum))[0]

lights = lifx.get_lights()

for L in sys.stdin:
    L = L.strip('\n')
    (addr, hue, saturation, brightness, kelvin) = L.split(' ')
    lifx.set_power(addr, True)
    lifx.set_color(addr, intfromhex(hue),
                         intfromhex(saturation),
                         intfromhex(brightness),
                         int(kelvin),
                         10000)


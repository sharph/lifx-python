#!/usr/bin/env python3

from binascii import hexlify
from struct import pack
import lifx

def tohex(datum):
    return str(hexlify(datum), encoding='utf-8')

lights = lifx.get_lights()

for L in lights:
    if L.power == False:
        continue
    line = tohex(L.addr) + ' '
    line += tohex(pack('>H', L.hue)) + ' '
    line += tohex(pack('>H', L.saturation)) + ' '
    line += tohex(pack('>H', L.brightness)) + ' '
    line += str(L.kelvin)
    print(line)

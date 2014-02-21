#!/usr/bin/env python3

import lifx
from time import time

program = [ [ [ 0xb693, 0xffff, 0x0000, 3500, 0 ],
              [ 0x105a, 0xffff, 0x0000, 3500, 0 ],
              '...',
              0 ],
            [ [ 0xb693, 0xffff, 0x19c6, 3500, 20000 ],
              [ 0x105a, 0xffff, 0x7bed, 3500, 15000 ],
              'Welcome to the LIFX-python demo program.',
              15 ],
            [ [ 0x2666, 0xbc36, 0xffff, 3500, 30000 ],
              [ 0xa5af, 0xe835, 0xffff, 3500, 30000 ],
              'We can switch from scene to scene.',
              30 ],
            [ [ 0x0000, 0x0000, 0xffff, 6500, 10000 ],
              [ 0x0000, 0x0000, 0xffff, 6500, 10000 ],
              "And we'll leave with 6500K white.",
              15 ] ]

lights = lifx.get_lights()

lights[0].set_power(True)
if len(lights) > 1:
    lights[1].set_power(True)

for step in program:
    lights[0].set_color(*step[0])
    if len(lights) > 1:
        lights[1].set_color(*step[1])
    print(step[2])
    start = time()
    while time() - start < step[3]:
        lifx.pause(3)
        lights[0].get_state()
        print(lights[0])
        if len(lights) > 1:
            lights[1].get_state()
            print(lights[1])

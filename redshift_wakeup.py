#!/usr/bin/env python3

import astral
import datetime
import lifx

# config

day_kelvin = 6500
night_kelvin = 3000

lightlist = [] # a list of lights to adjust. if [], adjust all

wakeup = True
wakeup_hour = 7
wakeup_min = 40
# 0mon 1tues 2weds 3thu 4fri 5sat 6sun
wakeup_days = [ 0, 1, 2, 3, 4 ]

redshift = True # adjust color temp when not waking up
only_white_lights = True # only adjust lights where saturation is 0


fade_time = 60 * 1000  # 60 seconds

city = 'Philadelphia'

region = 'Pennsylvania'

lat = 0.0
lon = 0.0

tz = ''

#####

a = astral.Astral()
a.solar_depression = 'civil'

try:
    city = a[city]
except NameError:
    print("City not found. Make sure lat long and timezone are defined.")
    city = astral.Location( (city, region, lat, lon, 0, tz) )

d = datetime.datetime.today()

sun = city.sun(local=True, date=d)

now = datetime.datetime.now(sun['dawn'].tzinfo)
wakeup = datetime.time(wakeup_hour, wakeup_min, 0, 0, sun['dawn'].tzinfo)
wakeup = datetime.datetime.combine(now, wakeup)
wakeup_end = wakeup + datetime.timedelta(minutes=10)

if now < sun['dawn']:
    period = 'night'
    target = night_kelvin
elif now < sun['sunrise']:
    period = 'sunrise'
    total_seconds = (sun['sunrise'] - sun['dawn']).total_seconds()
    time_since_dawn = (now - sun['dawn']).total_seconds()
    difference = day_kelvin - night_kelvin
    target = int(night_kelvin + \
             (float(time_since_dawn) / float(total_seconds) * difference))
elif now < sun['sunset']:
    period = 'day'
    target = day_kelvin
elif now < sun['dusk']:
    period = 'sunset'
    total_seconds = (sun['dusk'] - sun['sunset']).total_seconds()
    time_since_sunset = (now - sun['sunset']).total_seconds()
    difference = night_kelvin - day_kelvin
    target = int(day_kelvin + \
             (float(time_since_sunset) / float(total_seconds) * difference))
else:
    period = 'night'
    target = night_kelvin

print(period, target)

if now.weekday() in wakeup_days:
    print("today is a wakeup day")

if now < wakeup or now > wakeup_end or now.weekday() not in wakeup_days:
    wakeup = False

lights = lifx.get_lights()

for light in lights:
    if len(lightlist) > 0 and light.addr not in lightlist:
        print("skipping light %s. not in list", (light.get_addr(), ))
        continue
    if wakeup:
        if light.power == False:
            print("turning on %s" % (light.get_addr(),) )
            light.set_power(True)
            light.set_color(0, 0, 0, target, 0)
        print("setting %s to full brightness" % (light.addr,) )
        light.set_color(light.hue, 0, 0xffff, target, fade_time)
    elif (not only_white_lights or light.saturation == 0) and \
             light.kelvin != target and redshift:
        print("adjusting %s" % (light.get_addr(), ) )
        light.set_color(light.hue, 0, light.brightness, target, fade_time)
    else:
        print("skipping light %s" % (light.get_addr(), ))

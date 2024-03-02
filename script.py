#!/usr/bin/env python
import time

from parkertree.remote import Client
from parkertree.simulation import DisplaySimulator
from parkertree.animations import *
from parkertree.datastore import LEDDB

# This is a 2d sim, load the data from view 0
led_db = LEDDB("data/led_db.pickle")
led_data = led_db.getView(0)

t = Client("192.168.1.199", 3544)
t.clear()
#sim = DisplaySimulator(led_data)
circleblast = RainbowCircleBlaster(led_data)
strobe = Strobe(led_data)
wipe = RainbowWipe(led_data)
rb_fade = RainbowFade(led_data)

effects = [ 
    RainbowCircleBlaster(led_data),
    Strobe(led_data),
    RainbowWipe(led_data),
    RainbowFade(led_data),
    #SineChase(300)
    ]

unused_pixels = [ x for x in range(300) ]
for pixel in led_data:
    unused_pixels.remove(pixel.id)

while True:
    effect = random.choice(effects)
    for frame in effect:
        t.setString(frame.pixel_data)
    for p in unused_pixels:
        t.setLed(p, 0,0,0)

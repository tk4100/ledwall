#!/usr/bin/env python
import time
import random

from treecontrol import TreeController

tree = TreeController(300)

leds = [ x for x in range(0,301) ]
while True:
    led = random.choice(leds)
    r = random.choice([ x for x in range(255) ])
    g = random.choice([ x for x in range(255) ])
    b = random.choice([ x for x in range(255) ])
    
    tree.setLed(led, r, g, b)

    time.sleep(0.025)

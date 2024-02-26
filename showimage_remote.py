#!/usr/bin/env python
from PIL import Image
import sys
import numpy as np
import time

from xmasdata import XmasStrand
from remote import Client

d = XmasStrand()
t = Client("192.168.1.199", 3544)

min_x, min_y, max_x, max_y = d.getBounds(0)

print("Processing images...")
images = []
for imgfile in sys.argv[1:]:
    img = Image.open(imgfile)#.convert('RGB')
    img = img.rotate(-90)
    img = img.transpose(Image.FLIP_LEFT_RIGHT)
    img = img.resize((max_x-min_x, max_y-min_y))
    img = np.asarray(img)

    pixeldata = []
    for led in d.views[0]:
        try:
            r,g,b = img[led.x-min_x][led.y-min_y]
            pixeldata.append((led.id,r,g,b))
        except:
            continue

    images.append(pixeldata)

print("Beginning display")
while True:
    for pixeldata in images:
        #for pixel in pixeldata:
        #    led,r,g,b = pixel
        #    t.setLed(led,r,g,b)
        t.setString(pixeldata)

print("done")
time.sleep(10000)

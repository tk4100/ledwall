#!/usr/bin/env python
import sys
import numpy as np
import time
import random

from remote import Client
from animations import Animation,SineChase

t = Client("192.168.1.199", 3544)
fb = SineChase(300)
fb.setColor(Animation.WHITE)

while True:
    for frame in fb:
        s = time.time()
        t.setString(frame.pixel_data)
        e = time.time()
       
        # sleep off however much time is left after displaying the
        # last frame
        d = e-s
        if d < frame.display_time:
            time.sleep(frame.display_time - d)
        elif False:
            lag = d - frame.display_time
            print(f"Can't keep up!  Lagged by {lag}s")

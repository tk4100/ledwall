#!/usr/bin/env python
import time

from parkertree.simulation import DisplaySimulator
from parkertree.animations import Colors,SineChase
from parkertree.datastore import LEDDB

# This is a 2d sim, load the data from view 0
led_db = LEDDB("data/led_db.pickle")
led_data = led_db.getView(0)

print(led_data)

t = DisplaySimulator(led_data)
fb = SineChase(300)
fb.setColor(Colors.WHITE)

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
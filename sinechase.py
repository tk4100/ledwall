#!/usr/bin/env python
import time

from parkertree.simulation import DisplaySimulator
from parkertree.animations import Colors,SineChase
from parkertree.datastore import LEDDB
from parkertree.remote import Client

# This is a 2d sim, load the data from view 0
led_db = LEDDB("data/led_db.pickle")
led_data = led_db.getView(0)

print(led_data)

#sim = DisplaySimulator(led_data)
client = Client("192.168.1.199", 3544)
fb = SineChase(300)
fb.setColor(Colors.TURQUOISE)

while True:
	for frame in fb:
		s = time.time()
		#sim.setString(frame.pixel_data)
		client.setString(frame.pixel_data)
		e = time.time()
	   
		# sleep off however much time is left after displaying the
		# last frame
		d = e-s
		if d < frame.display_time:
			time.sleep(frame.display_time - d)
		elif False:
			lag = d - frame.display_time
			print(f"Can't keep up!  Lagged by {lag}s")

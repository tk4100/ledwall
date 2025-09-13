import os
import pickle

class LED():
    def __init__(self, led_id, x, y):
        self.id = led_id
        self.x = x
        self.y = y
        self.rel_x = 0
        self.rel_y = 0
        
class View():
    def __init__(self, angle=0):
        try:
            self.angle = int(angle)
        except ValueError:
            print("Shit data, bro.")
            return(None)
        
        self.leds = {}
        self.max_x = 0
        self.max_y = 0
        self.min_x = 9999999
        self.min_y = 9999999

    def setPosition(self, led_id, x, y):
        try:
            x = int(x)
            y = int(y)
            led_id = int(led_id)
        except ValueError:
            print("Failed to add capture.")
            return(False)

        # track the corners of our rectangle
        self.max_x = max([self.max_x, x])
        self.max_y = max([self.max_y, y])
        self.min_x = min([self.min_x, x])
        self.min_y = min([self.min_y, y])

        self.leds[led_id] = LED(led_id, x, y)

    def calcRelatives(self):
        for led in self.leds.keys():
            self.leds[led].rel_x = self.leds[led].x - self.min_x
            self.leds[led].rel_y = self.leds[led].y - self.min_y

    def __len__(self):
        return(len(self.leds.keys()))

    def __getitem__(self, key):
        assert type(key) == type(0), f"Passed a bad index type for an LED.  Should be {type(0)}. Got {type(key)}"
        assert key >= 0, "Passed a bad index type for an LED.  Should be a positive integer."
        if key in self.leds.keys():

            return(self.leds[key])
        else:
            return(False)

    def __setitem__(self, key, value):
        if key in self.leds.keys():
            self.leds[key] = value
        else:
            print(f"LED ID {key} does not exist in this View()!")
            raise KeyError

    def __iter__(self):
        self.idx = 0
        self.calcRelatives()
        self.led_list = [ x for x in self.leds.keys() ]
        return(self)

    def __next__(self):
        try:
            r = self.leds[self.led_list[self.idx]]
            self.idx += 1
        except IndexError:
            raise StopIteration
        return(r)

class LEDDB():
    def __init__(self, data_file):
        self.datastore_path = data_file

        if os.path.exists(self.datastore_path):
            with open(self.datastore_path, 'rb') as fh:
                self.views = pickle.load(fh)
        else:
            self.views = {}

    def wipeDB(self):
        self.views = {}
        self.flush()

    def flush(self):
        with open(self.datastore_path, 'wb') as fh:
            pickle.dump(self.views, fh)

    # takes all the data we currently have and creates the largest
    def captureLED(self, angle, led_id, x, y):
        try:
            angle = int(angle)
            led_id = int(led_id)
            x = int(x)
            y = int(y)
        except ValueError:
            print("Bad data passed to captureLED")
            return(False)

        if angle not in self.views.keys():
            self.views[angle] = View(angle)

        self.views[angle].setPosition(led_id, x, y)
        
    def getView(self, angle):
        return(self.views[angle])

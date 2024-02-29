import numpy as np
import time
import random

# Animations are iterable for frames.  Frames are a delay value and an array of pixel data
class Frame():
    def __init__(self, num_pixels, display_time):
        self.pixel_data = [ (0,0,0,0) for x in range(num_pixels) ]
        self.display_time = display_time

    def setPixel(self, idx, c):
        self.pixel_data[idx] = c

    # pass a map, and this frame will transform pixel IDs as indicated.
    def remap(self, pixelmap):
        pass

    def reverse(self):
        self.pixel_data.reverse()

class Colors():
    RED = (255,0,0)
    GREEN = (0,192,0)
    BLUE = (0,0,192)
    YELLOW = (255,100,0)
    PURPLE = (192,0,255)
    WHITE = (255, 255, 255)
    WARM_WHITE = (255,164,128)
    BLACK = (0,0,0)

    XMAS_SET = [ RED, GREEN, BLUE, YELLOW, PURPLE ]
    ALL_RED = [ RED ]
    ALL_WHITE = [ WARM_WHITE ]
    RED_GREEN = [ RED, GREEN ]
    RED_WHITE = [ RED, WHITE ]

    COLORSETS = [ XMAS_SET, ALL_RED, ALL_WHITE, RED_GREEN, RED_WHITE ]
    

class Animation():
    F32HZ = 0.03125
    F25HZ = 0.040
    F10HZ = 0.100
    F1HZ  = 1.000

    def __init__(self, num_pixels):
        # setup calls to be overridden
        self.num_pixels = num_pixels
        self.reset()
        self.animate()

    def reset(self):
        self.frames = []

    def __iter__(self):
        self.idx = 0
        return(self)

    def __next__(self):
        try:
            ret = self.frames[self.idx]
            self.idx += 1
        except IndexError:
            raise StopIteration

        return(ret)

class SineChase(Animation):
    def setColor(self, color):
        self.c = color
        self.animate()

    def animate(self):
        from math import sin,radians

        self.reset()

        frames = 70
        peaks_per_tree = 50
        phase_step_per_pixel = (360 / self.num_pixels) * peaks_per_tree
        phase_step_per_frame = 360 / frames

        if hasattr(self, "c"):
            c = self.c
        else:
            c = Colors.WARM_WHITE

        root_phase = 0
        for i in range(frames):
            pixels = []
            phase = root_phase
            frame = Frame(self.num_pixels, Animation.F10HZ)
            for j in range(self.num_pixels):
                m = (sin(radians(phase)) + 1) / 2# yields a sinusoid with values between 0 and 1
                pixel = (j, int(c[0]*m), int(c[1]*m), int(c[2]*m))
                frame.setPixel(j,pixel)
                phase += phase_step_per_pixel
            self.frames.append(frame)
            root_phase += phase_step_per_frame 


# modulate amplitude and frequency (color) in opposite directions.
class QAMChase(Animation):
    pass

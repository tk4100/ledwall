import numpy as np
import time
import random
import colorsys

from parkertree.datastore import View

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

class Colors():
    RED = (255,0,0)
    DIM_RED = (64,0,0)
    GREEN = (0,192,0)
    BLUE = (0,0,192)
    YELLOW = (255,100,0)
    PURPLE = (192,0,255)
    WHITE = (255, 255, 255)
    COOL_WHITE = (192,255,255)
    WARM_WHITE = (255,164,128)
    GOLD = (255,215,0)
    TURQUOISE = (0,192,192)
    BLACK = (0,0,0)
    TURQUOISE = (0,192,192)
    PINK = (255,20,147)
    LIGHT_BLUE = (64,255,255)

    XMAS_SET = [ RED, GREEN, BLUE, YELLOW, PURPLE ]
    ALL_RED = [ RED ]
    ALL_WHITE = [ WARM_WHITE ]
    RED_GREEN = [ RED, GREEN ]
    RED_WHITE = [ RED, WHITE ]

    COLORSETS = [ XMAS_SET, ALL_RED, ALL_WHITE, RED_GREEN, RED_WHITE ]

# Animations are iterable for frames.  Frames are a delay value and an array of pixel data
class Frame():
    def __init__(self, num_pixels, display_time):
        self.pixel_data = [ (0,0,0,0) for x in range(num_pixels) ]
        self.display_time = display_time

    def setPixel(self, idx, c):
        try:
            #(f"Set pixel {idx} to color {c}")
            self.pixel_data[idx] = c
            return True
        except IndexError:
            print(f"Pixel {idx} is not known. Last known is {len(self.pixel_data)}")

    # pass a map, and this frame will transform pixel IDs as indicated.
    def remap(self, pixelmap):
        pass

    def reverse(self):
        self.pixel_data.reverse()

class TwoDFrame():
    def __init__(self, pixeldata, display_time, color=Colors.BLACK):
        self.display_time = display_time
    
        self.pixels = {}
        for pixel in pixeldata:
            self.pixels[pixel.id] = color
        
    def setPixel(self, pixel_id, color):
        self.pixels[pixel_id] = color
        
    def render(self):
        self.pixel_data = []
        i = 0
        for pix in self.pixels.keys():
            r = self.pixels[pix][0]
            g = self.pixels[pix][1]
            b = self.pixels[pix][2]
            self.pixel_data.append((pix, r, g, b))

class TwoDAnimation(Animation):
    def __init__(self, pixeldata, mode="overlay", framerate=Animation.F32HZ):
        self.mode = mode
        self.framerate = framerate
    
        self.loadData(pixeldata)
        self.reset()
        self.animate()
        
    def loadData(self, pixeldata):
        assert type(pixeldata) == type(View()), "2D animation requires a View() object.  Did you call leddb.getView())?"
        self.pixels = pixeldata

    def reset(self):
        self.frames = []

    def drawBlankFrames(self, count, color=Colors.BLACK):
        for i in range(count):
            frame = TwoDFrame(self.pixels, self.framerate, color)
            frame.render()
            self.frames.append(frame)

    def drawCircle(self, h, k, r, color):
        def inCircle(x, y):
            if (x - h)**2 + (y - k)**2 <= r**2:
                return True
            else:
                return False
        
        if len(self.frames) == 0:
            frame = TwoDFrame(self.pixels, self.framerate)
        else:
            frame = self.frames[-1]
            
        for pixel in self.pixels:
            if inCircle(pixel.x, pixel.y):
                frame.setPixel(pixel.id, color)
        
        frame.render()
        self.frames.append(frame)
        
    def drawVerticalLine(self, x, width, color):
        frame = TwoDFrame(self.pixels, self.framerate)
        for pixel in self.pixels:
            if pixel.x >= x and pixel.x <= x + width:
                frame.setPixel(pixel.id, color)
                
        frame.render()
        self.frames.append(frame)
                
class BarBlaster(TwoDAnimation):
    def animate(self):
        colors = [Colors.BLUE, Colors.BLACK, Colors.GOLD, Colors.TURQUOISE, Colors.PINK, Colors.BLACK, Colors.BLACK]
        self.band_width = 100
        self.x = self.pixels.min_x
        for phase in range(5):
            self.i = phase
            while self.x + self.band_width < self.pixels.max_x:
                self.drawVerticalLine(self.x, self.band_width, random.choice(colors))
                self.i += 1
                self.x += self.band_width
            
class Lightning(TwoDAnimation):
    def animate(self):
        colors = [Colors.LIGHT_BLUE, Colors.COOL_WHITE * 5, Colors.BLACK * 35]
        self.band_width = 75
        self.x = self.pixels.min_x
        for i in range(300):
            self.drawVerticalLine(random.choice(range(self.pixels.min_x, self.pixels.max_x - self.band_width)), self.band_width, random.choice(colors))

class Tunnel(TwoDAnimation):
    def animate(self):
        ring_width = 15
        middle_x = int((self.pixels.max_x - self.pixels.min_x) / 2) + self.pixels.min_x
        middle_y = int((self.pixels.max_y - self.pixels.min_y) / 2) + self.pixels.min_y

        hole_r = 0
        circle_r = ring_width
        while circle_r < self.pixels.max_x - middle_x and circle_r < self.pixels.max_y - middle_y:
            self.drawCircle(middle_x, middle_x, circle_r, Colors.GOLD)
            self.drawCircle(middle_x, middle_x, hole_r, Colors.BLACK)
            hole_r += ring_width
            circle_r += ring_width

class CircleBlaster(TwoDAnimation):
    def animate(self):
        self.framerate = Animation.F32HZ
        colors = [ Colors.RED ] * 10 + [ Colors.TURQUOISE ] + [ Colors.YELLOW ] * 10
        for i in range(100):
            x = random.choice(range(self.pixels.max_x))
            y = random.choice(range(self.pixels.max_y))
            r = random.choice(range(100,300,10))
            self.drawBlankFrames(1)
            self.drawCircle(x, y, r, random.choice(colors))

class RainbowCircleBlaster(TwoDAnimation):
    def animate(self):
        colors = []
        for h in range(360):
            r,g,b = colorsys.hsv_to_rgb(h/360.,1.0,1)
            r = int(r*255)
            g = int(g*255)
            b = int(b*255)
            colors.append((r,g,b))
        
        for i in range(100):
            x = random.choice(range(self.pixels.max_x))
            y = random.choice(range(self.pixels.max_y))
            r = random.choice(range(100,300,10))
            self.drawBlankFrames(1)
            self.drawCircle(x, y, r, random.choice(colors))
            
class Strobe(TwoDAnimation):
    def animate(self):
        strobe = [ Colors.COOL_WHITE ] * 10 + [ Colors.BLACK ] * 10
        for i in range(100):
            self.drawBlankFrames(1, random.choice(strobe))
            
class RainbowStrobe(TwoDAnimation):
    def animate(self):
        colors = []
        for h in range(360):
            r,g,b = colorsys.hsv_to_rgb(h/360.,1.0,1)
            r = int(r*255)
            g = int(g*255)
            b = int(b*255)
            colors.append((r,g,b))
            
        colors = colors + [ (0,0,0) ] * 60    
        
        for i in range(100):
            self.drawBlankFrames(1, random.choice(colors))

class RainbowWipe(TwoDAnimation):
    def animate(self):
        h = 55/255.
        s = 1.0
        v = 255/255.
        barwidth = 250
        loops = 3
        for Q in range(loops):
            for x in range(self.pixels.min_x, self.pixels.max_x, int(barwidth/10)):
                h = x % 360
                r,g,b = colorsys.hsv_to_rgb(h/360.,s,v)
                r = int(r*255)
                g = int(g*255)
                b = int(b*255)
                self.drawVerticalLine(x, barwidth, (r,g,b))
    
class RainbowFade(TwoDAnimation):
    def animate(self):
        h = 55/255.
        s = 1.0
        v = 255/255.
        for h in range(0, 360,10):
            r,g,b = colorsys.hsv_to_rgb(h/360.,s,v)
            r = int(r*255)
            g = int(g*255)
            b = int(b*255)
            self.drawBlankFrames(1, (r,g,b))

class SineChase(Animation):
    def setColor(self, color):
        self.c = color
        self.animate()

    def animate(self):
        from math import sin,radians

        self.reset()

        frames = 70
        peaks_per_tree = 18
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
            frame = Frame(self.num_pixels, Animation.F32HZ)
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

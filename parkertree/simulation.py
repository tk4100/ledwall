import time
import pickle
import pygame

class DisplaySimulator():
    def __init__(self, led_data):
        # load led data
        self.led_data = led_data
        self.led_count = len(self.led_data)
        
        # init pygame for display
        pygame.init()
        self.dot_dia = 5
        self.screen = pygame.display.set_mode((
            self.led_data.max_x+self.dot_dia * 4,
            self.led_data.max_y+self.dot_dia * 4
            ))
        self.clear()
        pygame.display.flip()

    def clear(self):
        self.screen.fill((32,32,32))
        for led in range(self.led_count):
            self.setLed(led, 0, 0, 0)
        self.show()

    def show(self):
        pygame.display.flip()

    def setLed(self, led, r, g, b):
        try:
            x = self.led_data[led].x + self.dot_dia * 2
            y = self.led_data[led].y + self.dot_dia * 2
        except AttributeError:
            return(False)
        pygame.draw.circle(self.screen, (r,g,b), (x,y), self.dot_dia)
        self.show()
        return(True)

    # takes an array of tuples (led_id, r, g, b)
    def setString(self, data):
        for led in data:
            self.setLed(led[0], led[1], led[2], led[3])
        self.show()

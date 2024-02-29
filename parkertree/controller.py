import time
import spidev
import struct
import RPi.GPIO as GPIO

class CMDClear():
    def __init__(self):
        self.cmd_id = 200
        self.wire_format = '<B'# yeah I know endianness makes no sense here.

    def getBytes(self):
        return(struct.pack(self.wire_format, self.cmd_id))

class CMDShow():
    def __init__(self):
        self.cmd_id = 30
        self.wire_format = '<B'# yeah I know endianness makes no sense here.

    def getBytes(self):
        return(struct.pack(self.wire_format, self.cmd_id))

class CMDSingle():
    def __init__(self, led_id, r, g, b):
        self.cmd_id = 10
        self.wire_format = '<BHBBB'
        try:
           self.id = int(led_id)
           self.r = int(r)
           self.g = int(g)
           self.b = int(b)
        except ValueError:
            print("Bad data passed for SingleLED!!")
            return(False)

        assert self.r >= 0 and self.r <= 255, f"R ({self.r}) invalid!"
        assert self.g >= 0 and self.g <= 255, f"G ({self.g}) invalid!"
        assert self.b >= 0 and self.b <= 255, f"B ({self.b}) invalid!"

        self.bytes = struct.pack(self.wire_format, self.cmd_id, self.id, self.r, self.g, self.b)

    def getBytes(self):
        return(self.bytes)

class CMDString():
    # data is a list of tuples of (led_id, r, g, b)
    def __init__(self, data):
        self.cmd_id = 20
        self.max_chunk = 90
        self.header_format = '<BB'
        self.ledstatus_format = '<HBBB'
        self.data = data

    # returns a list of bytestrings
    def getBytes(self):
        data = [[]]
        for datum in self.data:
            if len(data[-1]) >= self.max_chunk:
                data.append([])
            data[-1].append(datum)

        
        bytestrings = []
        for chunk in data:
            bytestrings.append(struct.pack(self.header_format, self.cmd_id, len(chunk)))
            for datum in chunk:
                led,r,g,b = datum
                bytestrings[-1] += struct.pack(self.ledstatus_format, led, r, g, b)

        return(bytestrings)

class DisplayController():
    def __init__(self):
        # SPI and SPI control setup
        self.s = spidev.SpiDev()
        self.s.open(0,0)
        self.s.max_speed_hz = 1000000
        self.spi_ready_pin = 11
        self.spi_guard_interval = 0.005
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.spi_ready_pin, GPIO.IN)

        # constants and init
        self.cmd_format = '<B'
        self.cmd_io_size = struct.calcsize(self.cmd_format)
        self.clear()

    def clear(self):
        clear = CMDClear()
        self.sendBytes(clear.getBytes())

    def show(self):
        show = CMDShow()
        self.sendBytes(show.getBytes())

    def waitSPI(self):
        return
        sleeptime = 0
        while not GPIO.input(self.spi_ready_pin):
            time.sleep(0.001)
            sleeptime += 0.001
        if sleeptime > 0:
            sleeptime *= 1000
            #print(f"slept for {sleeptime:.02f}ms")

    def sendBytes(self, bytestring):
        self.waitSPI()
        self.s.writebytes(bytestring)
        time.sleep(self.spi_guard_interval)

    def setLed(self, led, r, g, b):
        LED = CMDSingle(led, r, g, b)
        self.sendBytes(LED.getBytes())

    # takes an array of tuples (led_id, r, g, b)
    def setString(self, data):
        string = CMDString(data)
        bytestrings = string.getBytes()
        for bytestring in bytestrings:
            self.sendBytes(bytestring)
        self.show()

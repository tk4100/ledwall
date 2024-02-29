import zmq

class MessageSingle():
    def __init__(self, led, r, g, b):
        self.type = "single"
        self.led = led
        self.r = r
        self.g = g
        self.b = b

class MessageClear():
    def __init__(self):
        self.type = "clear"

class MessageOK():
    def __init__(self):
        self.type = "OK"

class MessageString():
    def __init__(self, pixeldata):
        self.type = "string"
        self.data = pixeldata

class Server():
    def __init__(self, port, numleds=300):
        import zmq
        from controller import DisplayController
        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.REP)
        self.sock.bind(f"tcp://*:{port}")

        self.tree = DisplayController(numleds)

        self.listen()

    def listen(self):
        while True:
            msg = self.sock.recv_pyobj()
            if(msg.type == "single"):
                self.tree.setLed(msg.led, msg.r, msg.g, msg.b)
                self.sock.send_pyobj(MessageOK())
            elif(msg.type == "clear"):
                self.tree.clear()
                self.sock.send_pyobj(MessageOK())
            elif(msg.type == "string"):
                self.tree.setString(msg.data)
                self.sock.send_pyobj(MessageOK())

class Client():
    def __init__(self, host, port):
        self.ctx = zmq.Context()
        self.sock = self.ctx.socket(zmq.REQ)
        self.sock.connect(f"tcp://{host}:{port}")

    def setLed(self, led, r, g, b):
        m = MessageSingle(led, r, g, b)
        self.sock.send_pyobj(m)
        res = self.sock.recv_pyobj()

    def setString(self, pixeldata):
        m = MessageString(pixeldata)
        self.sock.send_pyobj(m)
        res = self.sock.recv_pyobj()

    def clear(self):
        m = MessageClear()
        self.sock.send_pyobj(m)
        res = self.sock.recv_pyobj()

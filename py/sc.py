import pyOSC3

class SuperColliderContext:
    def __init__(self, host='127.0.0.1', port=57120):
        self.client = pyOSC3.OSCClient()
        self.client.connect((host, port))
        self.running_notes = {}

    def StopInst(self, inst_name):
        if inst_name in self.running_notes:
            msg = pyOSC3.OSCMessage()
            msg.setAddress("/gf_stop")
            msg.append(inst_name)
            self.client.send(msg)
            del self.running_notes[inst_name]

    def Play(self, timestamp, inst_name, inst_args):
        self.StopInst(inst_name)
        msg = pyOSC3.OSCMessage()
        msg.setAddress("/gf_play")
        msg.append("%0.6f" % timestamp)
        msg.append(inst_name)
        for name, ia in inst_args:
            msg.append(name)
            msg.append("%06.f" % ia)
        self.client.send(msg)
        self.running_notes[inst_name] = inst_args

    def StartClock(self, timestamp):
        msg = pyOSC3.OSCMessage()
        msg.setAddress("/gf_start_clock")
        msg.append("%0.6f" % timestamp)
        self.client.send(msg)

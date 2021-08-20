import util

class Instrument:
    def __init__(self, name):
        self.name = name

    def Play(self, ctx, args):
        pass

    def __str__(self):
        return "Instrument('%s')" % self.name

    def __repr__(self):
        return "instrument." + str(self)

class Note:
    def __init__(self, instrument, args, energy):
        self.instrument = instrument
        self.args = args
        self.energy = energy

    def Play(self, ctx):
        self.instrument.Play(ctx, args)

    def __str__(self):
        return "Note(%s, %s, %f)" % (self.instrument, util.StrList(self.args), self.energy)

    def __repr__(self):
        return "instrument.Note(%s, %s, %f)" % (repr(self.instrument), util.ReprList(self.args), self.energy)

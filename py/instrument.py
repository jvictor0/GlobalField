import util

class Instrument:
    def __init__(self, name):
        self.name = name

    def Play(self, ctx, timestamp, params):
        param_list = params.Gen(energy=None)
        ctx.sc_ctx.Play(timestamp, self.name, param_list)

    def __str__(self):
        return "Instrument('%s')" % self.name

    def __repr__(self):
        return "instrument." + str(self)

class Note:
    def __init__(self, instrument, params, energy):
        self.instrument = instrument
        self.params = params
        self.energy = energy

    def Play(self, ctx, timestamp):
        self.instrument.Play(ctx, timestamp, self.params)

    def __str__(self):
        return "Note(%s, %s, %f)" % (self.instrument, util.StrShortList(self.params.List()), self.energy)

    def __repr__(self):
        return "instrument.Note(%s, %s, %f)" % (repr(self.instrument), repr(self.params), self.energy)

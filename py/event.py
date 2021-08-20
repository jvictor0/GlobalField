import math
import util

class Position:
    def __init__(self, beat, num, den):
        self.beat = beat
        self.offset_numerator = num
        self.offset_denomonator = den
        self.Reduce()

    def Reduce(self):
        div = util.GCD(self.offset_numerator, self.offset_denomonator)
        self.offset_numerator = self.offset_numerator / div
        self.offset_denomonator = self.offset_denomonator / div

    def Energy(self, ctx):
        return ctx.OrdEnergy(self.offset_denomonator)

    def Diff(self, other):
        num = self.offset_numerator * other.offset_denomonator - other.offset_numerator * self.offset_denomonator
        den = self.offset_denomonator * other.offset_denomonator
        num += den * (self.beat - other.beat)
        return Duration(num, den)

    def FromStart(self):
        return Diff(self, Position(self.beat, 0, 1))

    def BeatSupgroupSize(self):
        return self.offset_denomonator

    def CrossMul(self, other):
        return (self.offset_numerator * other.offset_denomonator,
                other.offset_numerator * self.offset_denomonator)
    
    def __le__(self, other):
        a,b = self.CrossMul(other)
        return (self.beat, a) <= (other.beat, b)

    def __lt__(self, other):
        a,b = self.CrossMul(other)
        return (self.beat, a) < (other.beat, b)

    def __eq__(self, other):
        a,b = self.CrossMul(other)
        return (self.beat, a) == (other.beat, b)
    
    def __str__(self):
        return "Position(%d, %d, %d)" % (self.beat, self.offset_numerator, self.offset_denomonator)

    def __repr__(self):
        return "event." + str(self)

class Duration:
    def __init__(self, num, den):
        self.numerator = numerator
        self.denomonator = denomonator
        self.Reduce()

    def Reduce(self):
        div = util.GCD(self.numerator, self.denomonator)
        self.numerator = self.numerator / div
        self.denomonator = self.denomonator / div

    def AsDecimal(self):
        return float(self.numerator) / float(self.denomonator)
    
    def __str__(self):
        return "Duration(%d %d)" % (self.numerator, self.denomonator)

    def __repr__(self):
        return "event." + str(self)

class Event:
    def __init__(self, note, position):
        self.note = note
        self.position = position

    def Play(self):
        self.note.Play()

    def Dur(self, nxt):
        return nxt.Diff(self)

    def Energy(self, ctx):
        return self.note.energy * ctx.LogOrdEnergy(self.position.offset_denomonator)

    def __str__(self):
        return "Event(%s, %s)" % (self.note, self.position)
    
    def __repr__(self):
        return "event.Event(%s, %s)" % (repr(self.note), repr(self.position))

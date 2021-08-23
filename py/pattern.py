import time
import util
import event
import copy

class Beat:
    def __init__(self, beat, denomonator, events):
        self.beat = beat
        self.denomonator = denomonator
        self.events = events

    def Play(self, ctx):
        for e in self.events:
            e.Play(ctx)

    def EventsAt(self, pos):
        assert isinstance(pos, event.Position)
        return [e for e in self.events if e.position == pos]

    def Positions(self):
        for i in xrange(self.denomonator):
            yield event.Position(self.beat, i, self.denomonator)
    
    def Validate(self):
        all_gcd = 1
        for ix in xrange(len(self.events)):
            e = self.events[ix]
            assert e.position.beat == self.beat
            assert self.denomonator % e.position.offset_denomonator == 0
            if ix > 0:
                assert self.events[ix - 1].position <= e.position
            all_gcd = util.GCD(all_gcd, e.position.offset_denomonator)

    def AddEvent(self, event):
        new_events = [e for e in self.events if e.position < event.position]
        new_events += [event]
        new_events += [e for e in self.events if event.position <= e.position]
        self.events = new_events

    def AsAbsolute(self, abs_beat):
        result = copy.deepcopy(self)
        result.beat = abs_beat
        for e in result.events:
            e.position.beat = abs_beat
        return result
        
    def __str__(self):
        if len(self.events) == 0:
            return "Beat(%d, %d, [])" % (self.beat, self.denomonator)
        else:
            return "Beat\n(\n    %d, %d, \n    %s\n)" % (self.beat, self.denomonator, util.StrList(self.events))

    def __repr__(self):
        return "pattern.Beat(%d, %d, %s)" % (self.beat, self.denomonator, util.ReprList(self.events))


class PatternStats:
    def __init__(self, pattern=None):
        # denomonator_spectrum - A dict of arrays such that for primes p, denomonator_spectrum[p][i]
        # is the number of beats with denomonator divisible by p^i.
        #
        self.denomonator_spectrum = {}
        if pattern is not None:
            self.ReInit(pattern)

    def RecordDenomonator(self, p, e):
        if p not in self.denomonator_spectrum:
            assert e == 1, (p, e)
            self.denomonator_spectrum[p] = []
        while len(self.denomonator_spectrum[p]) < e:
            self.denomonator_spectrum[p].append(0)
        self.denomonator_spectrum[p][e - 1] += 1
            
    def ReInit(self, pattern):
        for b in pattern.beats:
            factors = util.Factor(b.denomonator)
            for p, pwr in factors.iteritems():
                if p not in self.denomonator_spectrum:
                    self.denomonator_spectrum[p] = []
                for i in xrange(pwr):
                    if len(self.denomonator_spectrum[p]) <= i:
                        self.denomonator_spectrum[p].append(0)
                    self.denomonator_spectrum[p][i] += 1

    def DenomonatorSpectrum(self, p, pwr):
        if p not in self.denomonator_spectrum:
            return 0
        if len(self.denomonator_spectrum[p]) <= pwr:
            return 0
        return self.denomonator_spectrum[p][pwr]
                    
    def Validate(self, pattern):
        stats_copy = PatternStats(pattern)
        assert stats_copy.denomonator_spectrum == self.denomonator_spectrum
                    
class Pattern:
    def __init__(self, energy, beats):
        self.pat_id = util.NextId()
        self.beats = beats
        self.stats = PatternStats(self)
        self.energy = energy

    def Play(self, ctx, start_beat=0):
        for b in self.beats:
            b.Play(ctx)

    def Validate(self):
        for ix in xrange(len(self.beats)):
            self.beats[ix].Validate()
            assert self.beats[ix].beat == ix
        self.stats.Validate(self)

    def Clone(self):
        result = copy.deepcopy(self)
        result.pat_id = util.NextId()
        return result

    def NumBeats(self):
        return len(self.beats)
    
    def __str__(self):
        return "Pattern\n(\n    %f,\n    %s\n)" % (self.energy, util.StrList(self.beats))

    def __repr__(self):
        return "pattern.Pattern(%f, %s)" % (self.energy, util.ReprList(self.beats))


def MakeEmpty(num_beats):
    beats = [Beat(b, 1, []) for b in xrange(num_beats)]
    return Pattern(0.0, beats)


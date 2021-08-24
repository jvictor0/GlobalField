import event
import util

import copy
import random

class MutationEnergyException:
    def __init__(self, required_energy, actual_energy):
        self.required_energy = required_energy
        self.actual_energy = actual_energy

    def MultRequired(self, factor):
        if self.required_energy is not None:
            self.required_energy *= factor
        if factor is None:
            self.required_energy = None
        return self

class Mutation(object):
    def __init__(self, base_pattern, new_pattern):
        self.base_pattern = base_pattern
        self.new_pattern = new_pattern
        self.energy = min(0.0, new_pattern.energy - base_pattern.energy)

    def Validate(self):
        pass
        
class DenomonatorMutation(Mutation):
    def __init__(self, base_pattern, new_pattern, beat, factor):
        super(DenomonatorMutation, self).__init__(base_pattern, new_pattern)
        self.beat = beat
        self.factor = factor
        
    def Validate(self):
        assert self.base_pattern.NumBeats() == self.new_pattern.NumBeats()
        for ix in xrange(self.base_pattern.NumBeats()):
            if ix == self.beat:
                assert self.base_pattern.beats[ix].denomonator * self.factor == self.new_pattern.beats[ix].denomonator
            else:
                assert self.base_pattern.beats[ix].denomonator == self.new_pattern.beats[ix].denomonator

class AddNotesMutation(Mutation):
    def __init__(self, base_pattern, new_pattern, new_events):
        super(AddNotesMutation, self).__init__(base_pattern, new_pattern)
        self.new_events = new_events

    def AddEvent(self, event):
        return AddNotesMutation(self.base_pattern, self.new_pattern, self.events + [event])        
        
class Mutator:
    def __init__(self, ctx, pattern):
        self.ctx = ctx
        self.pattern = pattern

    # Given a list of (score, obj) pairs, call fnc on each obj in roughly-but-not-exactly the order
    # of the score, until an object returns without raising a MutationEnergyException.  If no such
    # is found, re-raise the exception with the minimal required energy.
    #
    def TryForEach(self, lst, fnc):
        random.shuffle(lst)
        lst.sort()
        
        required_energy = None
        for score, obj in util.ExpoIterator(lst):
            try:
                return fnc(obj)
            except MutationEnergyException as e:
                if required_energy is None:
                    required_energy = e.required_energy
                elif e.required_energy is not None:
                    required_energy = min(required_energy, e.required_energy)

        raise MutationEnergyException(required_energy, self.ctx.MutationEnergy())
        
    def BeatDenomonatorScore(self, beat):
        factors = util.Factor(beat.denomonator)
        spectrum = self.pattern.stats.denomonator_spectrum
        score = 1.0
        for p, pws in spectrum.iteritems():
            this_pwr = factors.get(p, 0)
            assert this_pwr <= len(pws), (p, this_pwr, pws)
            if this_pwr < len(pws):
                score = score / self.ctx.OrdEnergy(pow(p, pws[this_pwr]))

        return score
        
    def IncreasePatternBeatDenomonator(self):
        beats_with_scores = [(self.BeatDenomonatorScore(b), b) for b in self.pattern.beats]

        try:
            return self.TryForEach(beats_with_scores, self.IncreaseBeatDenomonator)
        except MutationEnergyException as e:
            util.TraceDebug("Mutation", "Not enough energy to IncraseDenomonator.  Required %s has %f.",
                            e.required_energy, e.actual_energy)
            raise
        
    def IncreaseBeatDenomonator(self, beat):
        factors = util.Factor(beat.denomonator)
        possible = []
        min_energy = None
        for p in util.g_primes:
            pwr = factors.get(p, 0)
            required_energy = self.ctx.OrdEnergy(pow(p, pwr + 1))

            # Discount the required energy by the number of other beats which also have
            # this factor.
            #
            required_energy /= (self.pattern.stats.DenomonatorSpectrum(p, pwr) + 1)

            if min_energy is None:
                min_energy = required_energy
            else:
                min_energy = min(required_energy, min_energy)
                
            if required_energy < self.ctx.MutationEnergy():
                possible.append((required_energy, p))
            
        if len(possible) == 0:
            raise MutationEnergyException(required_energy, self.ctx.MutationEnergy())
        
        required_energy, p = random.choice(possible)

        new_pattern = self.pattern.Clone()
        new_beat = new_pattern.beats[beat.beat]
        old_denomonator = new_beat.denomonator
        new_pattern.stats.total_slots += old_denomonator * (p - 1)
        new_beat.denomonator *= p
        new_pattern.stats.RecordDenomonator(p, factors.get(p, 0) + 1)

        self.ctx.ConsumeMutationEnergy(required_energy)

        util.TraceDebug("Mutation", "Increasing denomonator %d * %d -> %d at cost %f (total %f).",
                        old_denomonator, p, new_beat.denomonator,
                        required_energy, self.ctx.MutationEnergy())
        
        return DenomonatorMutation(self.pattern, new_pattern, new_beat.beat, p)

    def BeatAddNoteScore(self, beat):
        score = 0.0

        # The score is the sum of the inverse ord energies for events of the beat.  Thus missing low-
        # energy slots will be favored, but beats with many events will be punished.  The final score
        # is divided by the denomonator, so that higher denomonators are favored.  This could be thought
        # of as a sort of average of the inverse ord energies.
        #
        for e in beat.events:
            score += e.note.energy / self.ctx.LogOrdEnergy(e.position.offset_denomonator)

        score /= beat.denomonator

        return score
    
    def AddPatternBeatNote(self):
        beats_with_scores = [(self.BeatAddNoteScore(b), b) for b in self.pattern.beats]

        try:
            return self.TryForEach(beats_with_scores, self.AddBeatNote)
        except MutationEnergyException as e:
            util.TraceDebug("Mutation", "Not enough energy for AddNote.  Required %s has %f.",
                            e.required_energy, e.actual_energy)
            raise

    def AddBeatNote(self, beat):
        positions_with_scores = []
        for pos in beat.Positions():
            score = sum([e.Energy(self.ctx) for e in beat.EventsAt(pos)])
            positions_with_scores.append((score, pos))

        return self.TryForEach(positions_with_scores, lambda pos: self.AddPositionNote(beat, pos))

    def AddPositionNote(self, beat, pos):
        notes_at_pos = [e.note for e in beat.EventsAt(pos)]

        # The energy of the event is the energy of the note times its positional log ord energy, so
        # the budget for a notes energy is the total budged / log ord energy.
        #
        position_cost = self.ctx.LogOrdEnergy(pos.offset_denomonator)
        energy_avail = self.ctx.MutationEnergy()
        note_energy_budget = energy_avail / position_cost
        
        try:
            new_note = self.ctx.GenerateNote(note_energy_budget, notes_at_pos)
        except MutationEnergyException as e:
            raise e.MultRequired(position_cost)

        new_event = event.Event(new_note, pos)

        new_pattern = self.pattern.Clone()
        new_pattern.beats[beat.beat].AddEvent(new_event)
        new_pattern.stats.total_notes += 1
        self.ctx.ConsumeMutationEnergy(new_event.Energy(self.ctx))

        util.TraceDebug("Mutation", "Adding beat at pos %d/%d at cost %f (total %f).",
                        pos.offset_numerator, pos.offset_denomonator,
                        new_event.Energy(self.ctx), self.ctx.MutationEnergy())
        
        return AddNotesMutation(self.pattern, new_pattern, [new_event])

    def DoMutation(self):
        add_first = random.choice([True, False])
        try:
            if add_first:
                return self.AddPatternBeatNote()
            else:
                return self.IncreasePatternBeatDenomonator()
        except MutationEnergyException as e:
            if not add_first:
                return self.AddPatternBeatNote()
            else:
                return self.IncreasePatternBeatDenomonator()
    
class MutationContext:
    def __init__(self, ctx, initial_energy=0):
        self.ctx = ctx
        self.energy = initial_energy

    def MutatePattern(self, pattern):
        mut = Mutator(self.ctx, pattern)
        return mut.DoMutation().new_pattern
            
    def AddEnergyAndMutate(self, energy):
        self.energy += energy
        first = True
        while first or random.choice([True, False]):
            first = False
            pattern = self.ctx.RandomActivePattern()
            try:                
                new_pattern = self.MutatePattern(pattern)
            except MutationEnergyException as e:
                return

            self.ctx.AddPattern(new_pattern)
    

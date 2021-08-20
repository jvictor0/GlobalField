import event
import util

import copy
import random

class MutationEnergyException:
    def __init__(self, required_energy, actual_energy):
        self.required_energy = required_energy
        self.actual_energy = actual_energy

class Mutation:
    def __init__(self, ctx, pattern):
        self.ctx = ctx
        self.pattern = pattern
        self.energy = 0

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

        raise MutationEnergyException(required_energy, self.energy)
        
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

        return self.TryForEach(beats_with_scores, self.IncreaseBeatDenomonator)
        
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
                
            if required_energy < self.energy:
                possible.append((required_energy, p))
            
        if len(possible) == 0:
            raise MutationEnergyException(required_energy, self.energy)
        
        required_energy, p = random.choice(possible)

        new_pattern = copy.deepcopy(self.pattern)
        new_beat = new_pattern.beats[beat.beat]
        new_beat.denomonator *= p
        new_pattern.stats.RecordDenomonator(p, factors.get(p, 0) + 1)

        self.energy -= required_energy
        
        return new_pattern

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

        return self.TryForEach(beats_with_scores, self.AddBeatNote)

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
        note_energy_budget = self.energy / self.ctx.LogOrdEnergy(pos.offset_denomonator)
        new_note = self.ctx.GenerateNote(note_energy_budget, notes_at_pos)
        new_event = event.Event(new_note, pos)

        new_pattern = copy.deepcopy(self.pattern)
        new_pattern.beats[beat.beat].AddEvent(new_event)
        self.energy -= new_event.Energy(self.ctx)
        assert self.energy > 0

        return new_pattern

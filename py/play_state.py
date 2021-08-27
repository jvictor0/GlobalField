import threading
import bisect
import random
import util

class Generation:
    def __init__(self, patterns, energy):
        self.energy = energy
        self.patterns = patterns

    def Validate(self):
        assert len(self.patterns) > 0
        for p in self.patterns:
            p.Validate()

def GenerationFromPattern(pattern):
    return Generation([pattern], pattern.energy)
            
class EnergyKeyWrapper:
    def __init__(self, array):
        self.array = array

    def __getitem__(self, i):
        return sself.array[i].energy

    def __len__(self):
        return len(self.array)

class LivePattern:
    def __init__(self, pattern, ix):
        self.pattern = pattern
        self.ix = ix

    def NumBeats(self):
        return len(self.pattern.beats)
    
class PlayState:
    def __init__(self, initial_generation, max_patterns=5):
        self.generations = [initial_generation]
        self.max_patterns = max_patterns
        self.lock = threading.Lock()
        self.live_pattern = None
        self.beat_ix = 0
        self.absolute_beat_ix = 0

    def Validate(self):
        for ix in xrange(len(self.generations)):
            self.generations[ix].Validate()
            assert len(self.generations[ix].patterns) <= self.max_patterns
            if ix > 0:
                assert self.generations[ix - 1].energy < self.generations[ix].energy

    def GetLatestGeneration(self):
        with self.lock:
            return self.generations[-1]

    def AddGeneration(self, new_generation):
        with self.lock:
            self.generations.append(new_generation)

    # RevertToEnergyState - Remove generations until a state with lower energy than the new
    # budget is found.
    #
    def RevertToEnergyState(self, energy_budget):
        with self.lock:
            ix = bisect.bisect_left(EnergyKeyWrapper(self.generations), energy_budget)
            self.generations = self.generations[0:min(ix, 1)]
    
    def AddPattern(self, pattern):
        with self.lock:
            latest_gen = self.generations[-1]
            new_patterns = [p for p in latest_gen.patterns]

            # If there is space in the latest generation, potentially append the new pattern.
            # Else replace a random pattern.
            # The new energy is either added or the difference (if positive).
            #
            if len(new_patterns) < self.max_patterns and random.choice([True, False]):
                new_patterns.append(pattern)
                new_energy = pattern.energy
            else:
                old_pattern_ix = random.randrange(len(new_patterns))
                old_energy = new_patterns[old_pattern_ix].energy
                new_patterns[old_pattern_ix] = pattern
                new_energy = min(0, pattern.energy - old_energy)

            self.generations.append(Generation(new_patterns, latest_gen.energy + new_energy))

    def ToAbsolute(self, beat):
        self.absolute_beat_ix += 1
        return beat.AsAbsolute(self.absolute_beat_ix - 1)
            
    def StartPattern(self, generation):
        self.beat_ix = 1
        new_live_ix = random.randrange(len(generation.patterns))
        util.TraceDebug("PlayState", "Starting new pattern %d.", new_live_ix)
        self.live_pattern = LivePattern(generation.patterns[new_live_ix], new_live_ix)
        return self.ToAbsolute(self.live_pattern.pattern.beats[0])

    # NextBeat - Return the next beat to be played.
    #
    def NextBeat(self):
        generation = self.GetLatestGeneration()

        # If the beat_ix is zero, pick a new pattern to start.
        #
        if self.beat_ix == 0 or self.beat_ix == self.live_pattern.NumBeats():
            return self.StartPattern(generation)
        
        # If in the middle of a pattern, see if it matches the current generation, and if so, use it.
        # If not, still use it, but only if the length matches.  If not, start a new pattern.
        #
        if self.live_pattern.ix < len(generation.patterns) :
            new_pattern = generation.patterns[self.live_pattern.ix]
            if new_pattern.pat_id == self.live_pattern.pattern.pat_id:
                self.beat_ix += 1
                return self.ToAbsolute(self.live_pattern.pattern.beats[self.beat_ix - 1])
            elif self.live_pattern.NumBeats() == len(generation.patterns[self.live_pattern.ix].beats):
                self.beat_ix += 1
                self.live_pattern = LivePattern(new_pattern, self.live_pattern.ix)
                return self.ToAbsolute(new_pattern.beats[self.beat_ix - 1])
                
        return self.StartPattern(generation)

        

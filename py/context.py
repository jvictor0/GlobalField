import util
import math
import mutation
import instrument
import sc
import play_state
import time
import random
import position_queue
import event
import threading

class PrimeOrdEnergy:
    def __init__(self, prime, base):
        self.prime = prime
        self.base = base

    def Energy(self, denom):
        energy = 1.0
        while denom % self.prime == 0:
            energy *= self.base
            denom /= self.prime

        return energy

class OrdEnergy:
    def __init__(self, prime_ords):
        self.prime_ords = prime_ords

    def Energy(self, denom):
        energy = 1.0
        for poe in self.prime_ords:
            energy *= poe.Energy(denom)

        return energy

x_default_ord_energy = OrdEnergy([
    PrimeOrdEnergy(2, 2.0),
    PrimeOrdEnergy(3, 8.0),
    PrimeOrdEnergy(5, 32.0),
    PrimeOrdEnergy(7, 256.0),
    PrimeOrdEnergy(11, 1024.0)])

class Context:
    def __init__(self,
                 ord_energy=x_default_ord_energy,
                 sc_host='127.0.0.1',
                 sc_port=57120,
                 secs_per_beat=1.0,
                 latency=0.25):
        self.ord_energy = ord_energy
        self.sc_ctx = sc.SuperColliderContext(sc_host, sc_port)
        self.clock_info = ClockInfo(secs_per_beat, latency)
        self.StartClock()
        self.play_state = None
        self.mutation_ctx = mutation.MutationContext(self)
        self.note_generator = None
        self.position_queue = position_queue.PositionQueue()

    def OrdEnergy(self, x):
        return self.ord_energy.Energy(x)

    def LogOrdEnergy(self, x):
        return math.log(math.exp(1) - 1.0 + self.OrdEnergy(x))

    def GenerateNote(self, energy_budget, existing_notes, pattern_stats):
        return self.note_generator.GenerateNote(energy_budget, existing_notes, pattern_stats)
        
    def PositionTimestamp(self, pos):
        return self.clock_info.PositionTimestamp(pos)

    def StartClock(self):
        self.clock_info.StartClock()
        self.sc_ctx.StartClock(self.clock_info.start_timestamp)

    def InitPlayState(self, **kwargs):
        self.play_state = play_state.PlayState(**kwargs)

    def WaitForBeat(self, beat):
        self.clock_info.WaitForBeat(beat)

    def NextBeat(self):
        self.clock_info.WaitForBeat(self.play_state.absolute_beat_ix)
        next_beat = self.play_state.NextBeat()

        # Record each event in the next beat in the position queue.
        #
        elems = []
        for e in next_beat.events:
            elems.append(position_queue.PositionQueueElem(
                self.clock_info.PositionTimestamp(e.position),
                self.play_state.live_pattern.pattern.pat_id,
                e.RelativePosition(next_beat.relative_beat)))
        self.position_queue.Add(elems)

        return next_beat

    def MutationEnergy(self):
        return self.mutation_ctx.energy

    def ConsumeMutationEnergy(self, delta):
        assert self.mutation_ctx.energy >= delta
        self.mutation_ctx.energy -= delta

    def AddMutationEnergy(self, delta):
        self.ConsumeMutationEnergy(-delta)

    def RandomActivePattern(self):
        latest_gen = self.play_state.GetLatestGeneration()
        return random.choice(latest_gen.patterns)

    def AddPattern(self, pattern):
        self.play_state.AddPattern(pattern)
        
class ClockInfo:
    def __init__(self, secs_per_beat=1.0, latency=0.25):
        self.secs_per_beat = secs_per_beat
        self.latency = latency
        self.start_timestamp = time.time()
        self.lock = threading.Lock()

    def StartClock(self):
        with self.lock:                    
            self.start_timestamp = time.time()
        
    def PositionTimestamp(self, pos):
        with self.lock:
            return self.start_timestamp + self.latency + self.secs_per_beat * pos.AsDecimal()

    # WaitForBeat - Sleep til 1 second before the beat_ix, not including latency.
    #
    def WaitForBeat(self, beat):
        with self.lock:
            beat_time = self.start_timestamp + self.secs_per_beat * beat
            sleep_time = max(beat_time - time.time() - 1.0, 0.0)
            
        time.sleep(sleep_time)

    def SetTempo(self, new_secs_per_beat):
        with self.lock:
            new_secs_per_beat = float(new_secs_per_beat)
            now = time.time()
            beats_since_start = (now - self.start_timestamp) / self.secs_per_beat
            self.start_timestamp = now - beats_since_start * new_secs_per_beat
            self.secs_per_beat = new_secs_per_beat

    def SetTempoBPM(self, new_bpm):
        self.SetTempo(60.0 / new_bpm)
            
    def GetBPM(self):
        return 60.0 / self.secs_per_beat

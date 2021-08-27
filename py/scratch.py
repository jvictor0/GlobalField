import context
import instrument
import reload
import event
import pattern
import play_state
import driver
import mutation
import note_generation

import instruments.tiks

def Reload():
    reload.Reload()

def MakeClicks(num_beats=8):
    beats = [pattern.Beat(i, 1,
                          [event.Event(
                              instrument.Note(
                                  instrument.Instrument("tik"),
                                  note_generation.InstrumentPlayParams({
                                      "freq": note_generation.ConstantParamDistribution(0.0)
                                  }),
                                  1.0),
                              event.Position(i, 0, 1))])
             for i in xrange(num_beats)]
    return pattern.Pattern(float(num_beats), beats)

def PlayClicks(num_beats=8):
    ctx = context.Context()
    pattern = MakeClicks(num_beats)
    generation = play_state.GenerationFromPattern(pattern)
    ctx.InitPlayState(initial_generation=generation)
    driver.DriverThread(ctx)

def DoTheThing(num_beats=4):
    ctx = context.Context()
    ctx.note_generator = instruments.tiks.const_tik_generator
    pattern = MakeClicks(num_beats)
    generation = play_state.GenerationFromPattern(pattern)
    ctx.InitPlayState(initial_generation=generation, max_patterns=5)
    driver.StartDriver(ctx)
    md = mutation.MutationDrip(ctx, period=4.0)
    md.Run()
    
if __name__ == "__main__":
    DoTheThing()

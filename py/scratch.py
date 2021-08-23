import context
import instrument
import reload
import event
import pattern
import play_state
import driver

def Reload():
    reload.Reload()

def MakeClicks(num_beats=8):
    beats = [pattern.Beat(i, 1,
                          [event.Event(
                              instrument.Note(instrument.Instrument("tik"), [], 1.0),
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
    pattern = MakeClicks(num_beats)
    generation = play_state.GenerationFromPattern(pattern)
    ctx.InitPlayState(initial_generation=generation, max_patterns=1)
    driver.StartDriver(ctx)
    driver.MutationREPL(ctx)
    
if __name__ == "__main__":
    DoTheThing()

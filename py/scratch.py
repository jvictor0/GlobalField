import context
import instrument
import reload
import event
import pattern
import play_state
import driver
import mutation
import note_generation

import instruments.guru_blog_drums

def Reload():
    reload.Reload()

def MakeClicks(num_beats=8, inst_gen=None):
    beats = [pattern.Beat(i, 1,
                          [event.Event(
                              inst_gen.GenerateNote(float("inf"), [], pattern.PatternStats()),
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
    ctx.note_generator = instruments.guru_blog_drums.three_tone_drummer
    pattern = MakeClicks(num_beats, inst_gen=instruments.guru_blog_drums.hh)
    generation = play_state.GenerationFromPattern(pattern)
    ctx.InitPlayState(initial_generation=generation, max_patterns=5)
    driver.StartDriver(ctx)
    md = mutation.MutationDrip(ctx, period=4.0)
    md.Run()
    
if __name__ == "__main__":
    DoTheThing()

import context
import instrument
import reload
import event
import pattern

def Reload():
    reload.Reload()

def MakeClicks(num_beats=8):
    beats = [pattern.Beat(i, 1,
                          [event.Event(
                              instrument.Note(instrument.Instrument("tik"), [], 1.0),
                              event.Position(i, 0, 1))])
             for i in xrange(num_beats)]
    return pattern.Pattern(beats)

def PlayClicks(num_beats=8):
    ctx = context.Context()
    pattern = MakeClicks(num_beats)
    for b in pattern.beats:
        for e in b.events:
            e.Play(ctx)

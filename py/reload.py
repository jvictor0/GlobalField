import util
import event
import pattern
import instrument
import context
import mutation
import driver
import play_state
import sc

import sys

def Reload():
    reload(util)
    reload(event)
    reload(pattern)
    reload(instrument)
    reload(context)
    reload(mutation)
    reload(sc)
    return reload(sys.modules[__name__])

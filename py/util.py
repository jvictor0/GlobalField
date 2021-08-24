import random
import threading
import time
import datetime
import threading

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

try:
    assert g_utilInitialized
except NameError:
    g_utilInitialized = False

def GCD(x, y):
    while y != 0:
        x_mod_y = x % y
        x = y
        y = x_mod_y
    return x

def StrIndent(obj):
    return str(obj).replace("\n", "\n    ")

def StrList(lst):
    result = "[\n    " + ",\n    ".join(map(StrIndent, lst)) + "\n]"
    result = result.replace("\n","\n    ")
    return result

def StrShortList(lst):
    return "[" + ",".join(map(str, lst)) + "]"

def ReprList(lst):
    return "[" + ",".join(map(repr, lst)) + "]"

if not g_utilInitialized:
    g_primes = [2,3,5,7,11]

def Factor(x):
    result = {}
    for p in g_primes:
        pwr = 0
        while x % p == 0:
            pwr += 1
            x = x / p

        if pwr > 0:
            result[p] = pwr

    # UNDONE: add primes to g_primes...
    #
    assert x == 1, x
    
    return result
            
def ExpoIterator(lst, prob=0.5):
    while len(lst) > 0:
        ix = 0
        while ix + 1 < len(lst) and random.uniform(0, 1) < prob:
            ix += 1
        yield lst[ix]
        del lst[ix]

if not g_utilInitialized:
    g_nextId = 0
    g_nextIdLock = threading.Lock()

def NextId():
    global g_nextId
    with g_nextIdLock:
        g_nextId += 1
        return g_nextId
    
if not g_utilInitialized:
    g_logLevels = {
        "Mutation": 0
    }

    g_levels = ["DEBUG", "INFO", "WARNING"]

    g_logLock = threading.Lock()
    
def Trace(level, tag, msg, *largs):
    if level >= 2 or g_logLevels[tag] <= level:
        with g_logLock:
            print "%s [%s] %s: %s" % (timestamp(), tag, g_levels[level], msg % tuple(largs))

def TraceDebug(tag, msg, *largs):
    Trace(0, tag, msg, *largs)

def TraceInfo(tag, msg, *largs):
    Trace(1, tag, msg, *largs)

def TraceWarning(tag, msg, *largs):
    Trace(2, tag, msg, *largs)

g_utilInitialized = True



    

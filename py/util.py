import random

def GCD(x, y):
    while y != 0:
        x_mod_y = x % y
        x = y
        y = x_mod_y
    return x

def StrList(lst):
    return "[" + ",".join(map(str, lst)) + "]"

def ReprList(lst):
    return "[" + ",".join(map(repr, lst)) + "]"

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

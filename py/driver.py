import threading

def DriverThread(ctx):
    assert ctx.play_state is not None, "call InitPlayState"
    ctx.StartClock()
    while True:
        beat = ctx.NextBeat()
        beat.Play(ctx)

def MutationREPL(ctx):
    while True:
        energy = raw_input("add energy: ")
        try:
            energy = float(energy)
            assert energy >= 0            
        except Exception as e:
            print "fuck you", e
            continue
        ctx.mutation_ctx.AddEnergyAndMutate(energy)

def StartDriver(ctx):
    t = threading.Thread(target=DriverThread, args=(ctx,))
    t.start()

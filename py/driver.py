
def DriverThread(ctx):
    assert ctx.play_state is not None, "call InitPlayState"
    ctx.StartClock()
    while True:
        beat = ctx.NextBeat()
        beat.Play(ctx)

import util

def SerializeBeat(beat):
    beat = beat.WithUsedDenomonator()
    denomonator = beat.denomonator
    buckets = [beat.EventsAt(p) for p in beat.Positions()]
    assert len(buckets) == denomonator
    pows_of_two = 0

    d = denomonator
    while d % 2 == 0:
        pows_of_two += 1
        d /= 2

    is_binary = d == 1

    if is_binary:
        notes_occupied = 2 ** pows_of_two
    else:
        notes_occupied = 2 ** (pows_of_two + 1)
            
    note_type = 4 * notes_occupied

    result = ""
    ix = 0
    while ix < denomonator:
        if ix != 0:
            result += ", "
                
        note_length = 1
        pows_of_ix = pows_of_two if ix == 0 else util.PowsOf(2, ix)
        max_note_length = 2 ** min(pows_of_two, pows_of_ix)
        while ix + note_length < denomonator and note_length < max_note_length:
            if len(buckets[ix + note_length]) == 0:
                note_length += 1
            else:
                break

        while not util.IsPowOf(2, note_length):
            note_length -= 1
            
        if len(buckets[ix]) == 0:
            result += "B4"
        elif len(buckets[ix]) == 1:
            result += buckets[ix][0].note.render_note
        else:
            result += "(%s)" % " ".join([e.note.render_note for e in buckets[ix]])

        note_value = note_type / note_length
        result += "/%d" % note_value

        if len(buckets[ix]) == 0:
            result += "/r"
                
        ix += note_length

    return {
        "is_binary" : is_binary,
        "notes" : result,
        "notes_occupied" : notes_occupied,
        "num_notes" : denomonator,
    }

def SerializePattern(pattern):
    return {
        "energy" : pattern.energy,
        "beats" : [SerializeBeat(b) for b in pattern.beats]
    }

def SerializeGeneration(generation):
    return {
        "energy" : generation.energy,
        "patterns" : [SerializePattern(p) for p in generation.patterns]
    }

def SerializeContext(ctx):
    return {
        "mutation_energy" : ctx.MutationEnergy(),
        "current_generation" : SerializeGeneration(ctx.play_state.GetLatestGeneration())
    }


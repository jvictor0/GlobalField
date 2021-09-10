import util

def ValAndDots(note_length):
    if util.IsPowOf(2, note_length):
        return note_length, 0
    elif note_length % 3 == 0 and util.IsPowOf(2, note_length / 3):
        return 2 * note_length / 3, 1
    elif note_length % 7 == 0 and util.IsPowOf(2, note_length / 7):
        return 2 * note_length / 7, 2
    else:
        return None

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
    max_note_length = 2 ** pows_of_two
    
    notes = []
    ix = 0
    while ix < denomonator:
        note = ""

        note_length = 1
        
        while ix + note_length < denomonator and note_length < max_note_length:
            if len(buckets[ix + note_length]) == 0:
                note_length += 1
            else:
                break

        while not ValAndDots(note_length):
            note_length -= 1

        note_pre_value, dots = ValAndDots(note_length)
            
        if len(buckets[ix]) == 0:
            note += "B4"
        elif len(buckets[ix]) == 1:
            note += buckets[ix][0].note.render_note
        else:
            note += "(%s)" % " ".join([e.note.render_note for e in buckets[ix]])

        note_value = note_type / note_pre_value
        note += ("/%d" % note_value) + ("." * dots)        

        if len(buckets[ix]) == 0:
            note += "/r"

        notes.append(note)
        ix += note_length

    pre_rest = None
    ix = 0
    if notes[ix][-2:] == "/r":
        pre_rest = notes[ix]
        ix += 1
        while notes[ix][-2:] == "/r":
            pre_rest += ", " + notes[ix]
            ix += 1

    post_rest = None
    pix = len(notes) - 1
    if notes[pix][-2:] == "/r":
        post_rest = notes[pix]
        pix -= 1
        while notes[pix][-2:] == "/r":
            post_rest = notes[pix] + ", " + post_rest
            pix -= 1

    pix += 1
    assert ix < pix

    main_notes = ", ".join(notes[ix:pix])

    beam_groups = []
    if pre_rest is not None:
        beam_groups.append({"notes": pre_rest, "beam": False})

    beam_groups.append({"notes": main_notes, "beam": pix - ix > 1})

    if post_rest is not None:
        beam_groups.append({"notes": post_rest, "beam": False})
                
    return {
        "is_binary" : is_binary,
        "notes" : beam_groups,
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

function renderPattern(eltId, pattern)
{
    document.getElementById(eltId).innerHTML = "";
    const VF = Vex.Flow;
    
    var vf = new VF.Factory({renderer: {elementId: eltId}});
    var score = vf.EasyScore();
    var system = vf.System();

    var beats = pattern["beats"]
    var notes = null;
    for (var i = 0; i < beats.length; i++)
    {
        if (i == 0)
        {
            notes = renderBeat(score, beats[i]);
        }
        else
        {
            notes = notes.concat(renderBeat(score, beats[i]))
        }
    }

    system.addStave({
        voices: [score.voice(notes)]
    }).addTimeSignature(beats.length.toString() + "/4");

    vf.draw();
}

function renderBeat(score, beat)
{
    var notes = null;
    for (var i = 0; i < beat["notes"].length; i++)
    {
        var this_notes = score.notes(beat["notes"][i]["notes"])
        if (beat["notes"][i]["beam"])
        {
            this_notes = score.beam(this_notes, {autoStem: true})
        }

        if (i == 0)
        {
            notes = this_notes
        }
        else
        {
            notes = notes.concat(this_notes)
        }
    }
    
    if (beat["is_binary"])
    {
        return notes;
    }
    else
    {
        return score.tuplet(notes, {
            ratioed: false,
            notes_occupied: beat["notes_occupied"],
            num_notes: beat["num_notes"]
        });    
    }
}

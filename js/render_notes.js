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
    if (beat["notes_occupied"] == 1 && beat["num_notes"] == 1)
    {
        return score.notes(beat["notes"])
    }
    else if (beat["is_binary"])
    {
        return score.beam(score.notes(beat["notes"]))
    }
    else
    {
        return score.tuplet(score.beam(
            score.notes(beat["notes"]),
            {
                ratioed: false,
                notes_occupied: beat["notes_occupied"],
                num_notes: beat["num_notes"]
            }));
    }
}

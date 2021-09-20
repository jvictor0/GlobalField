function renderAllPatterns(elt_id, patterns)
{    
    document.getElementById(elt_id).innerHTML = "";

    const VF = Vex.Flow;
    
    for (var i = 0; i < patterns.length; i++)
    {
        var renderer = new VF.Renderer(document.getElementById(elt_id),
                                       VF.Renderer.Backends.SVG);
        renderer.resize(1000, 150);

        ctx = renderer.getContext()
        
        renderPattern(VF, ctx, patterns[i])
    }
}

function renderPattern(VF, ctx, pattern)
{
    var beats = pattern["beats"]

    var stave = new VF.Stave(10, 25, 800);
    stave.addTimeSignature(beats.length.toString() + "/4")

    var notes = [];
    var ornams = []
    for (var i = 0; i < beats.length; i++)
    {
        notes_and_ornams = renderBeat(VF, ctx, beats[i])
        notes = notes.concat(notes_and_ornams[0]);
        ornams = ornams.concat(notes_and_ornams[1]);
    }

    stave.setContext(ctx).draw();

    var voice = new VF.Voice({num_beats: beats.length, beat_value: 4});
    voice.addTickables(notes);

    var formatter = new VF.Formatter().joinVoices([voice]).format([voice], 800);

    voice.draw(ctx, stave);
    ornams.forEach(function(b) {b.setContext(ctx).draw()});
}

function renderBeat(VF, ctx, beat)
{
    var notes = [];
    var ornams = []
    for (var i = 0; i < beat["notes"].length; i++)
    {
        var current_beam = []
        var this_notes = beat["notes"][i]["notes"];
        for (var j = 0; j < this_notes.length; j++)
        {
            var note = this_notes[j];
            stave_note = new VF.StaveNote(note);
            if (note["is_current"])
            {
                stave_note.setStyle({fillStyle:"red"});
            }
            
            // Add the dots, since vexflow won't do it for us.
            //
            for (var k = 0; k < note["dots"]; k++)
            {
                stave_note.addModifier(0, new VF.Dot());
            }

            current_beam.push(stave_note);
        }

        notes = notes.concat(current_beam);
        
        if (beat["notes"][i]["beam"])
        {
            ornams.push(new VF.Beam(current_beam));
        }
    }
    
    if (!beat["is_binary"])
    {
        ornams.push(new VF.Tuplet(notes, {
            ratioed: false,
            notes_occupied: beat["notes_occupied"],
            num_notes: beat["num_notes"]
        }));
    }

    return [notes, ornams];
}

function renderScalarMetrics(elt_id, metrics)
{
    var result = "";
    for (let k in metrics)
    {
        result += "<p>" + k + ": " + metrics[k].toString() + "</p>";
    }

    document.getElementById(elt_id).innerHTML = result;
}

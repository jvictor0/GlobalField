from note_generation import *
import instrument
import util

bd = SingleInstrumentGenerator(
    instrument.Instrument("guru_blog_bd"),
    note_energy = 2.5,
    render_note = "F4",
    population_energy = util.Line(1.0, 1.0),
    params = InstrumentComposeParams({}))

clap = SingleInstrumentGenerator(
    instrument.Instrument("guru_blog_clap"),
    render_note = "B4",
    params = InstrumentComposeParams({}))

crash = SingleInstrumentGenerator(
    instrument.Instrument("guru_blog_crash"),
    note_energy = 10.0,
    render_note = "G5",
    population_energy = util.ExpoCurve(1.0, 2.0, 1.0),
    params = InstrumentComposeParams({}))

ding = SingleInstrumentGenerator(
    instrument.Instrument("guru_blog_ding"),
    render_note = "F5",
    params = InstrumentComposeParams({}))

hh = SingleInstrumentGenerator(
    instrument.Instrument("guru_blog_hh"),
    render_note = "E5",
    params = InstrumentComposeParams({}))

sn = SingleInstrumentGenerator(
    instrument.Instrument("guru_blog_sn"),
    render_note = "C5",
    note_energy = 5.0,
    population_energy = util.ExpoCurve(1.0, 2.0, 0.75),
    params = InstrumentComposeParams({}))

tom = SingleInstrumentGenerator(
    instrument.Instrument("guru_blog_tom"),
    render_note = "A4",
    params = InstrumentComposeParams({}))

three_tone_drummer = NoteGenerator({
    "bd" : bd,
    "sn" : sn,
    "hh" : hh })

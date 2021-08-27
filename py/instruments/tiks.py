from note_generation import *
import instrument

const_tik_generator = SingleInstrumentGenerator(
    instrument.Instrument("tik"),
    params = InstrumentComposeParams({
        "freq" : GaussianParamComposeDistribution(1200.0, 500.0)
    }))


    

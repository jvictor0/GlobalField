import util
import random
import mutation
import instrument

class ParamDistribution(object):
    def __init__(self, is_compose, **hyper_params):
        self.is_compose = is_compose
        self.hyper_params = hyper_params

    def Gen(self, energy):
        pass

    def __getitem__(self, hpname):
        return self.hyper_params[hpname]

class ParamComposeDistribution(ParamDistribution):
    def __init__(self, **hyper_params):
        super(ParamComposeDistribution, self).__init__(True, **hyper_params)

class ParamPlayDistribution(ParamDistribution):
    def __init__(self, **hyper_params):
        super(ParamPlayDistribution, self).__init__(False, **hyper_params)
    
class ConstantParamDistribution(ParamDistribution):
    def __init__(self, x):
        is_compose = isinstance(x, ParamDistribution)
        super(ConstantParamDistribution, self).__init__(is_compose, x=x)

    def Gen(self, energy):
        return self["x"]
    
class GaussianParamPlayDistribution(ParamPlayDistribution):
    def __init__(self, mu, sigma):
        super(GaussianParamPlayDistribution, self).__init__(mu=mu, sigma=sigma)

    def Gen(self, energy):
        return random.normalvariate(self["mu"], self["sigma"])

class GaussianParamComposeDistribution(ParamComposeDistribution):
    def __init__(self, mu, sigma):
        super(GaussianParamComposeDistribution, self).__init__(mu=mu, sigma=sigma)

    def Gen(self, energy):
        return ConstantParamDistribution(random.normalvariate(self["mu"], self["sigma"]))
    
class InstrumentPlayParams:
    def __init__(self, params):
        self.params = params

    def __getitem__(self, param_name):
        return self.params[param_name]

    def List(self):
        return self.params.keys()

    def Gen(self, energy):
        result = []
        for p, pd in self.params.iteritems():
            result.append((p, pd.Gen(energy)))
        return result

class InstrumentComposeParams:
    def __init__(self, params):
        self.params = params
        for k in self.params:
            if not self.params[k].is_compose:
                self.parans[k] = ConstantParamDistribution(self.params[k])
            assert self.params[k].is_compose

    def __getitem__(self, param_name):
        return self.params[param_name]

    def List(self):
        return self.params.keys()

    def GenPlayParams(self, energy):
        return InstrumentPlayParams({
            name : mp.Gen(energy)
            for name, mp in self.params.iteritems()
        })
    
class SingleInstrumentGenerator:
    def __init__(self,
                 instrument,
                 params,
                 note_energy = 1.0,
                 render_note = "B4",
                 population_energy=util.Const(1.0),
                 collision_costs=None):
        self.instrument = instrument
        self.params = params
        self.population_energy = population_energy
        if collision_costs is None:
            collision_costs = {}
        self.collision_costs = collision_costs
        self.note_energy = note_energy
        self.render_note = render_note
                 
    def Cost(self, existing_notes, population):
        energy_cost = self.population_energy(population)
        for note in existing_notes:
            if self.instrument.name == note.instrument.name:
                return None
            
            if note.instrument.name in self.collision_costs:
                
                if self.collision_costs[note.instrument.name] is None:
                    return None

                energy_cost *= self.collision_costs[note.instrument.name]
    
        return energy_cost * self.note_energy

    def GenerateNote(self, energy_budget, existing_notes, pattern_stats):        
        population = pattern_stats.InstPopulation(self.instrument)
        cost = self.Cost(existing_notes, population)
        if cost is None or energy_budget < cost:
            raise mutation.MutationEnergyException(cost, energy_budget)

        params = self.params.GenPlayParams(energy_budget - cost)
        return instrument.Note(self.instrument, params, self.render_note, cost)
            
class NoteGenerator:
    def __init__(self, instrument_generators):
        self.instrument_generators = instrument_generators

    def GenerateNote(self, energy_budget, existing_notes, pattern_stats):
        sigs = [(1.0, sig) for name, sig in self.instrument_generators.iteritems()]
        return mutation.TryForEach(
            energy_budget,
            sigs,
            lambda s: s.GenerateNote(energy_budget, existing_notes, pattern_stats))
        

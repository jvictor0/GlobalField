import util
import math
import mutation
import instrument

class PrimeOrdEnergy:
    def __init__(self, prime, base):
        self.prime = prime
        self.base = base

    def Energy(self, denom):
        energy = 1.0
        while denom % self.prime == 0:
            energy *= self.base
            denom /= self.prime

        return energy

class OrdEnergy:
    def __init__(self, prime_ords):
        self.prime_ords = prime_ords

    def Energy(self, denom):
        energy = 1.0
        for poe in self.prime_ords:
            energy *= poe.Energy(denom)

        return energy

x_default_ord_energy = OrdEnergy([
    PrimeOrdEnergy(2, 2.0),
    PrimeOrdEnergy(3, 8.0),
    PrimeOrdEnergy(5, 32.0),
    PrimeOrdEnergy(7, 256.0),
    PrimeOrdEnergy(11, 1024.0)])

class Context:
    def __init__(self, ord_energy=x_default_ord_energy):
        self.ord_energy = ord_energy

    def OrdEnergy(self, x):
        return self.ord_energy.Energy(x)

    def LogOrdEnergy(self, x):
        return math.log(math.exp(1) - 1.0 + self.OrdEnergy(x))

    def GenerateNote(self, energy_budget, existing_notes):
        if energy_budget < 1.0:
            raise mutation.MutationEnergyException(1.0, energy_budget)
        elif len(existing_notes) > 0:
            raise mutation.MutationEnergyException(None, energy_budget)
        else:
            return instrument.Note(instrument.Instrument("tik"), [], 1.0)

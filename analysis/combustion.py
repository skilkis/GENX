#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Performs a simple analysis for the fuel flow required to sustain combustion as well as computing air-fuel ratios """

from definitions import Attribute, Stage, FlowCondition
from directories import DIRS
from engine.specparser import SpecReader
from matplotlib import pyplot as plt
import os


class ChamberSpecs(SpecReader):

    __default_directory__ = DIRS['DATA_DIR']

    @Attribute
    def can_volume(self):
        """ Volume of the chamber where the main combustion process occurs in SI meter cubed [m^3] """
        return float(self.reader['v_cc'])

    @Attribute
    def pressure_loss(self):
        """ Total estimated hot and cold pressure loss in the combustion chamber expressed as the ratio between the
        outflow and inflow pressure """
        return float(self.reader['pr_cc'])

    @Attribute
    def air_mass_fractions(self):
        """ Determines the air mass flow fraction of the Primary Zone (PZ), Secondary Zone (SZ), and Dilution Zone (DZ).
        Therefore, multiplying by this factor will yield the mass flow of air in the given combustion chamber section

        :rtype: dict
        """
        return {key.split('_')[-1]: float(self.reader[key]) for key in ('amf_pz', 'amf_sz', 'amf_dz')}


class OperatingCondition(Stage):

    __slots__ = ['name', 'net_thrust', 'inflow', 'outflow', 'eta']

    def __init__(self, name, net_thrust, inflow, outflow, eta=0.99):
        self.name, self.net_thrust, self.inflow, self.outflow, self.eta = name, net_thrust, inflow, outflow, eta

    def __repr__(self):
        return '<OperatingCondition {}>'.format(self.name)

    @Attribute
    def fuel_flow(self):
        """ Fuel flow in the Combustion Chamber in SI kilogram per second [kg s^-1] (Tutorial 1, s. X) """
        return self.heat_output / (self.eta * self.lower_heating_value)

    @Attribute
    def equivalence_ratio(self):
        """ Determines the ratio which expresses if the current operating condition exhibits lean or rich combustion.
        An equivalence ratio <1 is lean combustion while >1 is rich.

        .. Note:: This is the overall equivalence ratio (average value of the entire combustion chamber)
        """
        return (self.fuel_flow / self.inflow.mass_flow) * self.afr_stoichiometric

    @Attribute
    def heat_output(self):
        """ Determines the heat output of the combustion chamber in SI Watt [w] """
        return self.inflow.mass_flow * self.specific_heat_gas * (self.outflow.t_total - self.inflow.t_total)


class CombustionAnalysis(object):

    def __init__(self, engine_name='PW4056'):
        """
        :param str engine_name: Sets the engine name used to access combustion chamber and experimental data files
        """
        self.engine_name = engine_name

    # TODO remove unecessary step of converting to a dictionary before the OperatingCondition objects are instantiated
    @Attribute
    def operating_conditions(self):
        """ Arranges the experimental data of the current engine in list of high-performance objects

        :rtype: list[OperatingCondition]
        """
        out_list = []
        for c in self.parse_data():
            name, net_thrust = c['condition'], c['net_thrust']
            inflow = FlowCondition(mass_flow=c['mass_flow_in'],
                                   p_total=c['p_in'],
                                   t_total=c['t_in'],
                                   station_number='3')
            outflow = FlowCondition(t_total=c['t_out'], station_number='4')
            out_list += [OperatingCondition(name=name, net_thrust=net_thrust, inflow=inflow, outflow=outflow)]
        return out_list

    @Attribute
    def chamber_specs(self):
        """ Specifications of the combustion chamber that is read from the filename specified by :py:attr:`engine_name`

        :rtype: ChamberSpecs
        """
        return ChamberSpecs(filename='{}.cfg'.format(self.engine_name))

    @Attribute
    def heat_density(self):
        """ Obtains the heat density of the combustion chamber in SI Watt per meter cubed [W/m^3] """
        pr_cc, v_cc = self.chamber_specs.pressure_loss, self.chamber_specs.can_volume
        return [cond.heat_output / (v_cc * (0.5 * (1. + pr_cc)) * cond.inflow.p_total)
                for cond in self.operating_conditions]

    @Attribute
    def equivalence_ratios(self):
        """ Calculates the equivalence ratio in the Primary (PZ), Secondary (SZ), and Dilution (DZ) zones

        :rtype: list[dict]
        """
        amf, oc = self.chamber_specs.air_mass_fractions, self.operating_conditions  # Localizing variables
        afr_st = self.operating_conditions[0].afr_stoichiometric
        return [{zone: afr_st * (c.fuel_flow/(frac * c.inflow.mass_flow)) for zone, frac in amf} for c in oc]

    def parse_data(self):
        """ Transforms the experimental data of the current engine into a dictionary containing flow properties at
        the inlet and outlet of the combustion chamber. These quantities are expressed in SI units.

        :rtype: list[dict]
        """
        with open(os.path.join(DIRS['DATA_DIR'], '{}_experiment.csv'.format(self.engine_name))) as f:
            try:
                lines = f.readlines()
                keys = [key for key in lines[0].split(',') if key != '\n']
                data = [[float(entry) if entry.replace('.', '').isdigit() else entry for i, entry in
                         enumerate(line.split(',')) if entry != '\n'] for line in lines[1:]]  # transforms .csv to dict
                data_dict = [{keys[i]: entry for i, entry in enumerate(condition)} for condition in data]
                return data_dict
            except Exception as e:
                # TODO add a more comprehensive input file reading/checking mechanism
                raise e


if __name__ == '__main__':
    obj = CombustionAnalysis()
    obj.parse_data()
    print(obj.heat_density)
    for c in obj.operating_conditions:
        print(c.equivalence_ratio)


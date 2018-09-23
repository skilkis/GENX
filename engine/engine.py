#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Contains all abstract class definitions  """

from specparser import SpecParser
from definitions import FlowCondition, Component
from components import *
import numpy as np

__author__ = 'San Kilkis'


class Engine(SpecParser):

    def __init__(self, filename='GE90.cfg', ideal_cycle=False, design_variable=None, design_range=None,
                 ambient=FlowCondition(corrected_mass_flow=1400.,
                                       mach=0.8,
                                       p_static=22632.,
                                       t_static=216.,
                                       medium='air')):
        """
        :param str filename: Filename w/ extension of desired engine
        :param bool ideal_cycle: Toggles if the compression and expansion processes are isentropic
        :param str design_variable: Specifies which design variable to investigate for the sensitivity analysis
        :param np.array design_range: Optionally set a range of values for the design variable
        :param FlowCondition ambient: Specifies the flow the engine is subject to
        :param:
        """

        super(Engine, self).__init__(filename)
        self.ideal_cycle = ideal_cycle
        self.design_variable = design_variable
        self.ambient = ambient

        # Converting Engine to be an ideal cycle
        if self.ideal_cycle:
            self.make_ideal()

        # Setting-up a range of design_variable values for the Sensitivity Analysis
        if design_variable is not None:
            if design_range is None:
                self.design_range = self.get_range()
            else:
                try:
                    ndim = design_range.ndim
                    if ndim == 1:
                        self.design_range = design_range
                    else:
                        raise ValueError("A {}D array for 'design_range' was provided,"
                                         " only 1D arrays are supported".format(ndim))
                except AttributeError:
                    raise AttributeError("'design_range' must be a 1D numpy array for the vectorized process")
            setattr(self, design_variable, self.design_range)  # Setting passed or created range for the design_variable
        else:
            self.design_range = design_range  # Sets to default value of None

    def make_ideal(self):
        """ Sets all efficiencies as well as the pressure ratio in the combustion chamber to 1.0 """
        # Fetching all engine specifications which need to set to 1.0
        ideal_attrs = self.get_eta_keys() + ['pr_cc']
        for entry in ideal_attrs:
            setattr(self, entry, 1.0)

    def get_range(self):
        """ Automatically obtains sensitivity analysis range for a variable if :py:attr:`design_range` is ``None`` """
        current_value = getattr(self, self.design_variable)
        n = 50
        if 'eta' in self.design_variable:
            upper = 1.0
            lower = 0.9
            return np.linspace(lower, upper, n)
        else:
            upper = 1.1 * current_value
            lower = 0.9 * current_value
            lower_range, step = np.linspace(lower, current_value, n // 2, retstep=True)
            upper_range = np.arange(current_value, upper, step)[1:]  # Ensures that current_value is present in output
            return np.append(lower_range, upper_range)

    @Component
    def inlet(self):
        return Inlet(ambient=self.ambient,
                     eta=self.eta_inlet)

    @Component
    def fan(self):
        return Fan(inflow=self.inlet.outflow,
                   eta=self.eta_fan,
                   pressure_ratio=self.pr_fan,
                   station_number='21')

    @Component
    def bypass(self):
        return Bypass(inflow=self.fan.outflow,
                      bypass_ratio=self.bypass_ratio)

    @Component
    def lpc(self):
        return Compressor(inflow=self.bypass.outflow_core,
                          eta=self.eta_lpc,
                          pressure_ratio=self.pr_lpc,
                          station_number='25')

    @Component
    def hpc(self):
        return Compressor(inflow=self.lpc.outflow,
                          eta=self.eta_hpc,
                          pressure_ratio=self.pr_hpc,
                          station_number='3')

    @Component
    def combustor(self):
        return CombustionChamber(inflow=self.hpc.outflow,
                                 eta=self.eta_cc,
                                 pressure_ratio=self.pr_cc,
                                 t_total_exit=self.combustion_temperature)

    @Component
    def lp_spool(self):
        return Spool(compressor_in=(self.fan, self.lpc),
                     eta=self.eta_mech)

    @Component
    def hp_spool(self):
        return Spool(compressor_in=self.hpc,
                     eta=self.eta_mech)

    @Component
    def hpt(self):
        return Turbine(inflow=self.combustor.outflow,
                       spool_in=self.hp_spool,
                       eta=self.eta_hpt,
                       station_number='45')

    @Component
    def lpt(self):
        return Turbine(inflow=self.hpt.outflow,
                       spool_in=self.lp_spool,
                       eta=self.eta_lpt,
                       station_number='5')

    @Component
    def nozzle_core(self):
        return Nozzle(inflow=self.lpt.outflow,
                      ambient=self.ambient,
                      eta=self.eta_nozzle,
                      nozzle_type=self.nozzle_type,
                      station_number=('7', '8'))

    @Component
    def nozzle_bypass(self):
        return Nozzle(inflow=self.bypass.outflow_bypass,
                      ambient=self.ambient,
                      eta=self.eta_nozzle,
                      nozzle_type=self.nozzle_type,
                      station_number=('16', '18'))

    # TODO make this more general, able to cope with less nozzles (maybe not bypassed)

    @property
    def thrust(self):
        """ Total Thrust force produced by the engine in SI Newton [N] """
        return self.nozzle_core.thrust + self.nozzle_bypass.thrust

    @property
    def sfc(self):
        """ Thrust Specific Fuel Consumption (TSFC) in SI gram per kilo-Newton second [g/kN s] """
        return (self.combustor.fuel_flow / self.thrust) * 1e6

    @classmethod
    def get_components(cls):
        return [value for value in vars(cls).values() if isinstance(value, Component)]

    def get_eta_keys(self):
        """ Provides a list of all efficiency keys by accessing the superclass :py:class:`SpecParser` dictionary

        :rtype: list[str]
        """
        return [key for key in vars(super(self.__class__, self)).keys() if 'eta' in key]


if __name__ == '__main__':
    obj = Engine(ideal_cycle=False, design_variable='eta_nozzle')
    print(obj.design_range)
    print(obj.sfc)
    print(obj.thrust)

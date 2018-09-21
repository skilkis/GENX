#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Contains all abstract class definitions  """

from specparser import SpecParser
from definitions import FlowCondition, Component
from components import *
import numpy as np
try:
    import ConfigParser as config
except ImportError:
    import configparser as config

__author__ = 'San Kilkis'


class Engine(SpecParser):

    def __init__(self, filename='GE90.cfg', isentropic=True, design_variable='eta_cc',
                 ambient_conditions=FlowCondition(mach=0.8, p_static=22632, t_static=216, medium='air')):
        """
        :param str filename: Filename w/ extension of desired engine
        :param bool isentropic: Toggles if the compression and expansion processes are isentropic
        :param str design_variable: Specifies which design variable to investigate
        :param FlowCondition inflow: Specifies the flow the engine is subject to
        """
        super(Engine, self).__init__(filename)
        self.isentropic = isentropic
        self.design_variable = design_variable
        self.ambient_conditions = ambient_conditions

        # Test Range Bounds for the Sensitivity Analysis
        upper, lower = self.get_bounds()
        self.test_range = np.linspace(lower, upper, 50)

    def get_bounds(self):
        """ Automatically obtains sensitivity analysis bounds for a variable """
        current_value = getattr(self, self.design_variable)
        upper, lower = 0.9 * current_value,  1.1 * current_value
        if 'eta' in self.design_variable:
            upper = 1.0
            lower = 0.9
        return upper, lower

    @Component
    def inlet(self):
        return Inlet(ambient=self.ambient_conditions,
                     eta=0.98)

    @Component
    def fan(self):
        return Fan(inflow=self.inlet.outflow,
                   eta=0.92,
                   pressure_ratio=1.6,
                   station_number='21')

    @Component
    def bypass(self):
        return Bypass(inflow=self.fan.outflow,
                      bypass_ratio=8.)

    @Component
    def lpc(self):
        return Compressor(inflow=self.bypass.outflow_core,
                          eta=0.9,
                          pressure_ratio=1.4,
                          station_number='25')

    @Component
    def hpc(self):
        return Compressor(inflow=self.lpc.outflow,
                          eta=0.9,
                          pressure_ratio=19,
                          station_number='3')

    @Component
    def combustor(self):
        return CombustionChamber(inflow=self.hpc.outflow,
                                 eta=0.99,
                                 pressure_ratio=0.96,
                                 t_total_exit=1450.)

    @Component
    def lp_spool(self):
        return Spool(compressor_in=(self.fan, self.lpc),
                     eta=0.99)

    @Component
    def hp_spool(self):
        return Spool(compressor_in=self.hpc,
                     eta=0.99)

    @Component
    def hpt(self):
        return Turbine(inflow=self.combustor.outflow,
                       spool_in=self.hp_spool,
                       eta=0.92,
                       station_number='45')

    @Component
    def lpt(self):
        return Turbine(inflow=self.hpt.outflow,
                       spool_in=self.lp_spool,
                       eta=0.92,
                       station_number='5')

    @Component
    def nozzle_core(self):
        return Nozzle(inflow=self.lpt.outflow,
                      ambient=self.ambient_conditions,
                      eta=0.98,
                      nozzle_type='convergent',
                      station_number=('7', '8'))

    @Component
    def nozzle_bypass(self):
        return Nozzle(inflow=self.bypass.outflow_bypass,
                      ambient=self.ambient_conditions,
                      eta=0.98,
                      nozzle_type='convergent',
                      station_number=('16', '18'))


    @property
    def sfc(self):
        """ Thrust Specific Fuel Consumption (TSFC) in SI gram per kilo Newton second [g/kN s] """
        return 'self.fuel_flow / self.thrust'


if __name__ == '__main__':
    obj = Engine()
    print(obj.eta_nozzle)
    print(obj.test_range)

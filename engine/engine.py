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

    def __init__(self, filename='GE90.cfg',
                 isentropic=True,
                 design_variable='eta_cc',
                 design_range=None,
                 ambient=FlowCondition(corrected_mass_flow=1400.,
                                       mach=0.8,
                                       p_static=22632,
                                       t_static=216,
                                       medium='air')):
        """
        :param str filename: Filename w/ extension of desired engine
        :param bool isentropic: Toggles if the compression and expansion processes are isentropic
        :param str design_variable: Specifies which design variable to investigate
        :param FlowCondition inflow: Specifies the flow the engine is subject to
        """
        super(Engine, self).__init__(filename)
        self.isentropic = isentropic
        self.design_variable = design_variable
        self.ambient = ambient

        # Test Range Bounds for the Sensitivity Analysis
        if design_range is None:
            upper, lower = self.get_bounds()
            self.design_range = np.linspace(lower, upper, 50)
            setattr(self, design_variable, self.design_range)

    def get_bounds(self):
        """ Automatically obtains sensitivity analysis bounds for a variable if  """
        current_value = getattr(self, self.design_variable)
        upper, lower = 0.9 * current_value,  1.1 * current_value
        if 'eta' in self.design_variable:
            upper = 1.0
            lower = 0.9
        return upper, lower

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

    # def plot_thrust(self):



if __name__ == '__main__':
    obj = Engine()
    print(obj.eta_cc)
    print(obj.combustor.fuel_flow)
    print(obj.thrust)
    print(obj.sfc)

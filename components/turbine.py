#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ADD DOC """

from definitions import Stage, FlowCondition

__author__ = 'San Kilkis'

# TODO add function for plotting line on TS diagram


class Turbine(Stage):

    def __init__(self, inflow, eta, spool_in, station_number):
        """

        :param inflow:
        :param eta:
        :param Spool spool_in: Spool to which the :py:class`Turbine` is attached
        :param str station_number: Station number corresponding to the end of the stage
        """
        self.inflow = inflow
        self.eta = eta
        self.spool_in = spool_in
        self.station_number = station_number

    @property
    def work_output(self):
        """ Convenience property that represents the work output of the :class:`Turbine` in SI Watt [W]. This quantity
        is equivalent to the work required to drive the compressor(s) on the same spool (mechanical losses are already
        accounted for in :class:`Spool`.

        :rtype: float
        """
        return self.spool_in.work_required

    @property
    def t_total(self):
        """ Total temperature at the end of the py:class:`Turbine` stage in SI Kelvin [K]. The temperature drop
        corresponds to the expansion process through which work can be extracted

        :rtype: float
        """
        return self.inflow.t_total - (self.work_output / (self.inflow.mass_flow * self.inflow.specific_heat))

    @property
    def p_total(self):
        """ Total pressure at the end of the Turbine stage in SI Pascal [Pa]. The total pressure in the system decreases
        proportionally to the decrease in total temperature

        :rtype: float
        """
        return self.inflow.p_total * ((1. + ((1. / self.eta) *
                                      ((self.t_total / self.inflow.t_total) - 1.)))
                                      ** (self.inflow.kappa / (self.inflow.kappa - 1.)))

    @property
    def outflow(self):
        """ Represents the flow conditions at the end of the Turbine """
        return FlowCondition(mass_flow=self.inflow.mass_flow,
                             t_total=self.t_total,
                             p_total=self.p_total,
                             medium='gas',
                             station_number=self.station_number)


if __name__ == '__main__':
    from inlet import Inlet
    from fan import Fan
    from bypass import Bypass
    from compressor import Compressor
    from combustion import CombustionChamber
    from spool import Spool
    ambient_conditions = FlowCondition(corrected_mass_flow=1400.,
                                       mach=0.8, t_static=216, p_static=22632, station_number='1', medium='air')
    inlet = Inlet(ambient=ambient_conditions, eta=0.98)
    fan = Fan(inflow=inlet.outflow, eta=0.92, pressure_ratio=1.6, station_number='21')
    bypass = Bypass(inflow=fan.outflow, bypass_ratio=8.)
    lpc = Compressor(inflow=bypass.outflow_core, eta=0.9, pressure_ratio=1.4, station_number='25')
    hpc = Compressor(inflow=lpc.outflow, eta=0.9, pressure_ratio=19, station_number='3')
    combustor = CombustionChamber(inflow=hpc.outflow, eta=0.99, pressure_ratio=0.96, t_total_exit=1450.)
    lp_spool = Spool(compressor_in=(fan, lpc), eta=0.99)
    hp_spool = Spool(compressor_in=hpc, eta=0.99)
    hpt = Turbine(inflow=combustor.outflow, spool_in=hp_spool, eta=0.92, station_number='45')
    lpt = Turbine(inflow=hpt.outflow, spool_in=lp_spool, eta=0.92, station_number='5')
    print(lpt.t_total)
    print(lpt.p_total)


    # print(obj.p_total)
    # print(obj.t_total)

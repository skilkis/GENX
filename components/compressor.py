#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ADD DOC """

from definitions import Stage, FlowCondition

__author__ = 'San Kilkis'

# TODO add function for plotting line on TS diagram


class Compressor(Stage):

    def __init__(self, inflow, eta, pressure_ratio, station_number):
        """

        :param inflow:
        :param eta:
        :param pressure_ratio: Pressure Ratio
        """
        self.inflow = inflow
        self.eta = eta
        self.pressure_ratio = pressure_ratio
        self.station_number = station_number

    @property
    def t_total(self):
        """ Total temperature is not constant across the fan """
        return self.inflow.t_total * (1 + (1/self.eta) *
                                      (((self.p_total / self.inflow.p_total)**((self.inflow.kappa - 1)
                                                                               / self.inflow.kappa)) - 1))

    @property
    def p_total(self):
        """ Total pressure changes proportionally across the fan as a multiple of the pressure ratio """
        return self.inflow.p_total * self.pressure_ratio

    @property
    def outflow(self):
        return FlowCondition(mass_flow=self.inflow.mass_flow,
                             t_total=self.t_total,
                             p_total=self.p_total,
                             medium='air',
                             station_number=self.station_number)


if __name__ == '__main__':
    from inlet import Inlet
    from fan import Fan
    from bypass import Bypass
    ambient_conditions = FlowCondition(corrected_mass_flow=1400.,
                                       mach=0.8, t_static=216, p_static=22632, station_number='1', medium='air')
    inlet = Inlet(inflow=ambient_conditions, eta=0.98)
    fan = Fan(inflow=inlet.outflow, eta=0.92, pressure_ratio=1.6, station_number='21')
    bypass = Bypass(inflow=fan.outflow, bypass_ratio=8.)
    lpc = Compressor(inflow=bypass.outflow_bypass, eta=0.9, pressure_ratio=1.4, station_number='25')
    hpc = Compressor(inflow=lpc.outflow, eta=0.9, pressure_ratio=19, station_number='3')
    print(hpc.p_total)
    print(hpc.t_total)

    # print(obj.p_total)
    # print(obj.t_total)

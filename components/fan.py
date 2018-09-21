#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ADD DOC """

from definitions import Stage, FlowCondition
from inlet import Inlet

__author__ = 'San Kilkis'

# TODO add function for plotting line on TS diagram


class Fan(Stage):

    def __init__(self, inflow, eta, pressure_ratio):
        """

        :param inflow:
        :param eta:
        :param pressure_ratio: Pressure Ratio
        """
        self.inflow = inflow
        self.eta = eta
        self.pressure_ratio = pressure_ratio

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
    def mass_flow_core(self):
        return self.inflow.mass_flow / (self.bypass_ratio + 1.)

    @property
    def mass_flow_bypass(self):
        return self.mass_flow_core * self.bypass_ratio

    @property
    def outflow(self):
        return NotImplementedError


if __name__ == '__main__':
    from definitions import FlowCondition
    ambient_conditions = FlowCondition(corrected_mass_flow=1400.,
                                       mach=0.8, t_static=216, p_static=22632, station_number='1', medium='air')
    inlet = Inlet(inflow=ambient_conditions, eta=0.98)
    obj = Fan(inflow=inlet.outflow, eta=0.92, pressure_ratio=1.6)
    print(obj.t_total)
    print(obj.p_total)

    # print(obj.p_total)
    # print(obj.t_total)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ADD DOC """

from definitions import Stage, FlowCondition
from inlet import Inlet

__author__ = 'San Kilkis'

# TODO add function for plotting line on TS diagram


class Bypass(Stage):

    def __init__(self, inflow, bypass_ratio):
        self.inflow = inflow
        self.bypass_ratio = bypass_ratio

    @property
    def t_total(self):
        """ Total temperature remains constant across the inlet """
        return self.inflow.t_total

    @property
    def mass_flow_core(self):
        return self.inflow.mass_flow / (self.bypass_ratio + 1.)

    @property
    def mass_flow_bypass(self):
        return self.mass_flow_core * self.bypass_ratio

    @property
    def p_total(self):
        """ Total pressure remains constant only distributed """
        return self.inflow.p_total

    @property
    def outflow(self):
        return NotImplementedError


if __name__ == '__main__':
    from definitions import FlowCondition
    ambient_conditions = FlowCondition(corrected_mass_flow=1400.,
                                       mach=0.8, t_static=216, p_static=22632, station_number='1', medium='air')
    inlet = Inlet(inflow=ambient_conditions, eta=0.98)
    obj = Bypass(inflow=inlet.outflow, bypass_ratio=8.0)
    print(obj.mass_flow_bypass)
    print(obj.mass_flow_core)

    # print(obj.p_total)
    # print(obj.t_total)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ADD DOC """

from definitions import Stage, FlowCondition
from inlet import Inlet
from fan import Fan

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
    def outflow_core(self):
        return FlowCondition(mass_flow=self.mass_flow_core,
                             t_total=self.t_total,
                             p_total=self.p_total,
                             station_number='21',
                             medium='air')

    @property
    def outflow_bypass(self):
        return FlowCondition(mass_flow=self.mass_flow_bypass,
                             t_total=self.t_total,
                             p_total=self.p_total,
                             station_number='13',
                             medium='air')


if __name__ == '__main__':
    from definitions import FlowCondition
    ambient_conditions = FlowCondition(corrected_mass_flow=1400.,
                                       mach=0.8, t_static=216, p_static=22632, station_number='1', medium='air')
    inlet = Inlet(ambient=ambient_conditions, eta=0.98)
    fan = Fan(inflow=inlet.outflow, eta=0.92, pressure_ratio=1.6, station_number='21')
    obj = Bypass(inflow=fan.outflow, bypass_ratio=8.)
    print(obj.mass_flow_bypass)
    print(obj.mass_flow_core)

    # print(obj.p_total)
    # print(obj.t_total)

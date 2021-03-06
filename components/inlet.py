#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ADD DOC """

from definitions import Stage, FlowCondition
from copy import deepcopy

__author__ = 'San Kilkis'

# TODO add function for plotting line on TS diagram


class AmbientInterface(Stage):

    def __init__(self, ambient):
        self.inflow = ambient

    @property
    def t_total(self):
        """ Total temperature remains constant across the interface """
        return self.inflow.t_total

    @property
    def p_total(self):
        """ Total pressure remains constant across the interface """
        return self.inflow.p_total

    @property
    def outflow(self):
        outflow = deepcopy(self.inflow)
        outflow.station_number = '1'
        return outflow


class Inlet(Stage):

    def __init__(self, inflow, eta):
        self.inflow = inflow
        self.eta = eta

    @property
    def t_total(self):
        """ Total temperature remains constant across the inlet """
        return self.inflow.t_total

    @property
    def p_total(self):
        p, eta, k, m = self.inflow.p_static, self.eta, self.inflow.kappa, self.inflow.mach
        return p * (1 + (eta * ((k - 1) / 2.) * m ** 2)) ** (k / (k - 1))

    @property
    def outflow(self):
        return FlowCondition(t_total=self.t_total, p_total=self.p_total, station_number='2',
                             mass_flow=self.inflow.mass_flow, medium='air')


if __name__ == '__main__':
    ambient_conditions = FlowCondition(mach=0.8, t_static=216., p_static=22632., station_number='1', medium='air',
                                       corrected_mass_flow=1400.)
    interface = AmbientInterface(ambient=ambient_conditions)
    obj = Inlet(inflow=interface.outflow, eta=0.98)
    print(obj.inflow.mass_flow)
    print(obj.p_total)
    print(obj.t_total)

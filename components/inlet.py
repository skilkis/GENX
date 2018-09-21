#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ADD DOC """

from definitions import Stage, FlowCondition

__author__ = 'San Kilkis'

# TODO add function for plotting line on TS diagram


class Inlet(Stage):

    def __init__(self, ambient, eta):
        self.ambient = ambient
        self.eta = eta

    @property
    def t_total(self):
        """ Total temperature remains constant across the inlet """
        return self.ambient.t_total

    @property
    def p_total(self):
        p, eta, k, m = self.ambient.p_static, self.eta, self.ambient.kappa, self.ambient.mach
        return p * (1 + (eta * ((k - 1) / 2.) * m ** 2)) ** (k / (k - 1))

    @property
    def outflow(self):
        return FlowCondition(t_total=self.t_total, p_total=self.p_total, station_number='2',
                             mass_flow=self.ambient.mass_flow, medium='air')


if __name__ == '__main__':
    ambient_conditions = FlowCondition(mach=0.8, t_static=216., p_static=22632., station_number='1', medium='air',
                                       corrected_mass_flow=1400.)
    obj = Inlet(ambient=ambient_conditions, eta=0.98)
    print(obj.ambient.mass_flow)
    print(obj.p_total)
    print(obj.t_total)

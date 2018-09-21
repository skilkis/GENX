#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Contains all abstract class definitions  """

from __future__ import division
from constants import *
from utils import Undefined
from math import sqrt

__author__ = 'San Kilkis'


class FlowCondition(Constants):

    __kwargs__ = None

    # Providing dummy attributes for the debugger, these are partially overwritten at run-time by the constructor
    mass_flow = Undefined('mass_flow')
    corrected_mass_flow = Undefined('corrected_mass_flow')
    mach = Undefined('mach')
    t_static = Undefined('t_static')
    t_total = Undefined('t_total')
    p_static = Undefined('p_static')
    p_total = Undefined('p_total')
    medium = Undefined('medium')
    station_number = Undefined('station_number')

    def __init__(self, **kwargs):
        """

        :param float mass_flow:
        :param float mach:
        :param float t_static:
        :param float p_static:
        :param str medium:
        :param float t_total:
        :param float p_total:
        :param str station_number:
        """
        self.__kwargs__ = kwargs
        for key, value in zip(kwargs.keys(), kwargs.values()):
            command = 'self.{} = {}'.format(key, "'{}'".format(value) if type(value) is str else value)
            exec command

    # def __repr__(self):
    #     return '<Undefined = {}>.format'

    @Attribute
    def kappa(self):
        """ Ratio of Specific Heat Selected Medium """
        if self.medium == 'air':
            return self.kappa_air
        elif self.medium == 'gas':
            return self.kappa_gas
        else:
            raise AttributeError("Data for the provided medium '{}' does not exist".format(self.medium))

    @Attribute
    def specific_heat(self):
        """ Specific Heat of the Selected Medium at Constant Pressure c_p in SI Joule per kilogram Kelvin [J/kg K] """
        if self.medium == 'air':
            return self.specific_heat_air
        elif self.medium == 'gas':
            return self.specific_heat_gas
        else:
            raise AttributeError("Data for the provided medium '{}' does not exist".format(self.medium))

    # TODO Add Attributes: Corrected Mass Flow if necessary otherwise mass flow

    @Attribute
    def corrected_mass_flow(self):
        """ Returns the mass flow corrected for pressure and temperature effects in SI kilogram per second [kg s^-1] """
        return self.mass_flow * self.c_ratio

    @Attribute
    def mass_flow(self):
        """ Actual mass flow in SI kilogram per second [kg s^-1] """
        return self.corrected_mass_flow / self.c_ratio

    @Attribute
    def t_total(self):
        return self.t_static * self.t_ratio

    @Attribute
    def p_total(self):
        return self.p_static * self.p_ratio

    @Attribute
    def t_static(self):
        return self.t_total / self.t_ratio

    @Attribute
    def p_static(self):
        return self.p_total / self.p_ratio

    @Attribute
    def t_ratio(self):
        """ Total Temperature to Static Temperature Ratio """
        return 1 + (((self.kappa - 1) / 2.) * self.mach**2)

    @Attribute
    def p_ratio(self):
        """ Total Pressure to Static Pressure Ratio """
        return (1 + (((self.kappa - 1) / 2.) * self.mach**2))**(self.kappa / (self.kappa - 1))

    @Attribute
    def c_ratio(self):
        """ Correction Ratio for obtaining the Corrected Mass Flow """
        numerator = sqrt(self.t_total / self.temperature_sl)
        denominator = self.p_total / self.pressure_sl
        return numerator / denominator

    @staticmethod
    def ensure_float(entry):
        return float(entry) if entry is not None or str else entry


class Stage(Constants):

    @Attribute
    def inflow(self):
        return NotImplementedError('Implement an __init__ method to obtain the FlowCondition at the start of the stage')

    @Attribute
    def outflow(self):
        return NotImplementedError('Implement methods to compute this parameter in sublcasses')


if __name__ == '__main__':
    obj = FlowCondition(mach=0.8, p_total=101325, medium='air')
    print(obj.p_static)

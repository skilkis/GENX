#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from constants import *
from utils import Undefined
import numpy as np

__author__ = 'San Kilkis'


class Component(property):
    """ Renames the :py:class:`property` to be able to organize all engine components and retrieve them easily """

    def __repr__(self):
        return "<'{}' {} object at {}>".format(self.fget.__name__,
                                               self.__class__.__name__,
                                               hex(id(self)))


class FlowCondition(Constants):

    __kwargs__ = None

    # Providing dummy attributes for the debugger, these are partially overwritten at run-time by the constructor
    mass_flow = Undefined('mass_flow')
    corrected_mass_flow = Undefined('corrected_mass_flow')
    mach = Undefined('mach')
    velocity = Undefined('velocity')
    t_static = Undefined('t_static')
    t_total = Undefined('t_total')
    p_static = Undefined('p_static')
    p_total = Undefined('p_total')
    medium = Undefined('medium')
    rho = Undefined('rho')
    station_number = Undefined('station_number')

    # TODO Finish documentaiton
    def __init__(self, **kwargs):
        """

        :param float mass_flow:
        :param float mach:
        :param float velocity:
        :param float t_static:
        :param float p_static:
        :param str medium:
        :param float t_total:
        :param float p_total:
        :param float rho: Density of the substance in SI kilogram per meter cubed [kg/m^3]
        :param str station_number:
        """
        self.__kwargs__ = kwargs
        for key, value in zip(kwargs.keys(), kwargs.values()):
            setattr(self, key, value)

    # TODO add a nice representation for visualization in debugger and print statements
    # def __repr__(self):
    #     return '<Undefined = {}>.format'

    @Attribute
    def velocity(self):
        """ Computes flow velocity from the mach number if available in SI meter per second [m/s] """
        return self.mach * np.sqrt(self.kappa * self.gas_constant * self.t_static)

    @Attribute
    def rho(self):
        """ Computes the density from the static pressure and temperature in SI kilogram per meter cubed [kg/m^3] """
        return self.p_static / (self.gas_constant * self.t_static)

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
        numerator = np.sqrt(self.t_total / self.temperature_sl)
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

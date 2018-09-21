#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Provides all derived/non-derived inputs of to be used later in performance calculations """

from utils import Attribute

__author__ = 'San Kilkis'
__all__ = ['Constants', 'Attribute']

# working_dir = os.path.dirname(os.path.realpath(__file__))

# TODO consider making use of https://docs.python.org/2/library/trace.html for dependency tracking


class Constants(object):

    # TODO re-document class
    """ An OOP Version of the above constants to use for the following part of this assignment, supporting lazy
     evaluation where not every attribute or property will be triggered at run-time, thus increasing performance """

    # TODO re-incorporate singleton after code verification
    # __instance__ = None
    #
    # def __new__(cls, *args, **kwargs):
    #     """ Stops the :py:class:`Base` from instantiating more than once, if an instance exists in the current process
    #     that instance is then returned as a pointer for all other sub-classes. """
    #     if cls.__instance__ is None:
    #         cls.__instance__ = super(Constants, cls).__new__(cls, *args, **kwargs)
    #     return cls.__instance__

    @Attribute
    def g(self):
        """ Gravitational Acceleration in SI meter per second [m /s]"""
        return 9.81

    @Attribute
    def rho_sl(self):
        """ ISA Sea Level Atmospheric Density in SI kilogram per meter cubed [kg/m^3]"""
        return 1.225

    @Attribute
    def temperature_sl(self):
        """ ISA Sea Level Temperature in SI Kelvin [K] """
        return 288.15

    @Attribute
    def pressure_sl(self):
        """ ISA Sea Level Pressure in SI Pascal [Pa] """
        return 101325.

    @Attribute
    def specific_heat_air(self):
        """ Specific Heat of Air at Constant Pressure c_p in SI Joule per kilogram Kelvin[J/kg K] """
        return 1000.

    @Attribute
    def specific_heat_gas(self):
        """ Specific Heat of Fuel/Air Mixture at Constant Pressure c_p in SI Joule per kilogram Kelvin [J/kg K] """
        return 1150.

    @Attribute
    def kappa_air(self):
        """ Ratio of Specific Heats of Air [-] """
        return 1.4

    @Attribute
    def kappa_gas(self):
        """ Ratio of Specific Heats for the Fuel/Air Mixture [-] """
        return 1.33

    @Attribute
    def lower_heating_value(self):
        """ Lower Heating Value (LHV) of Kerosene in SI Mega Joule [MJ] """
        return 43. * 1e6

    @Attribute
    def gas_constant(self):
        """ Individual Gas Constant of Air in SI Joule per kilogram Kelvin [J/kg K] """
        return 287.05


if __name__ == '__main__':
    obj = Constants()

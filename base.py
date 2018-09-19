#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Provides all derived/non-derived inputs of the CH-53D Helicopter to be used later in performance calculations """

from utils import Attribute
import os
try:
    import ConfigParser as config
except ImportError:
    import configparser as config

try:
    from __builtin__ import raw_input
except ImportError:
    from builtins import input as raw_input


__author__ = 'San Kilkis'

# working_dir = os.path.dirname(os.path.realpath(__file__))

# TODO Remove the following attributes and put them into OOP for lazy-evaluation

# TODO consider making use of https://docs.python.org/2/library/trace.html for dependency tracking

# TODO make engine specs loader from .cfg


class Entry(object):

    __slots__ = ['value', 'unit']

    def __init__(self, value, unit=None):
        self.value = value
        self.unit = unit

    def __get__(self, instance, owner):
        return self.value

    def __repr__(self):
        return '%1.4f [%s]' % (self.value, self.unit)

    def __add__(self, other):
        return self.value + other

    def __sub__(self, other):
        return self.value - other

    def __div__(self, other):
        return self.value / other

    def __mul__(self, other):
        return self.value * other

    def __eq__(self, other):
        return self.value == other

    def __float__(self):
        return self.value

    def __int__(self):
        return self.value

    def __abs__(self):
        return self.value


class Base(object):

    """ An OOP Version of the above constants to use for the following part of this assignment, supporting lazy
     evaluation where not every attribute or property will be triggered at run-time, thus increasing performance """

    __engine_file__ = 'data\GE90.cfg'
    __instance__ = None

    def __new__(cls, *args, **kwargs):
        """ Stops the constants class from initializing more than once, if an instance exists in the current process
        that instance is simply returned """
        if cls.__instance__ is None:
            cls.__instance__ = super(Base, cls).__new__(cls, *args, **kwargs)
        return cls.__instance__

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
        """ Specific Heat of Fuel/Air Mixture at Constant Pressure c_p in SI Joule per kilogram Kelvin[J/kg K] """
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
    def engine_data(self):
        if self.__engine_file__ is None:
            selected_engine = raw_input("Provide an engine file for computations: ")
            selected_engine = selected_engine if selected_engine.endswith('.cfg') else selected_engine + '.cfg'
            engine_files = os.listdir('data')
            if selected_engine in engine_files:
                self.__engine_file__ = os.path.join('data', selected_engine)
            else:
                raise IOError("No file named '{}' could be found within 'data'".format(selected_engine))
        cfg = config.SafeConfigParser()
        cfg.read(self.__engine_file__)
        return cfg._sections.copy()


if __name__ == '__main__':
    obj = Base()
    print(obj.engine_data['ambient_conditions']['t_static'])
    obj2 = Base()
    print(obj2.__instance__)
    # print(obj.g)
    # print(obj.rho_sl)
    # obj.g = 20
    # print(obj.g)
    # print(obj.rho_sl)
    # print('As you can see there is no dependency tracking yet, be careful!')


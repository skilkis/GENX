#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Contains all abstract class definitions  """

from constants import *
import os
try:
    import ConfigParser as config
except ImportError:
    import configparser as config

__author__ = 'San Kilkis'

# TODO finish documenting, mach, p_static, t_static


class SpecParser(object):

    __default_directory__ = 'data'

    def __init__(self, filename='GE90.cfg'):
        """
        :param str filename: Filename w/ extension of desired engine
        """
        self.filename = filename
        self.__name__ = filename.split('.')[0]

    def __repr__(self):
        return "<'{}' {} object at {}>".format(self.__name__,
                                               self.__class__.__name__,
                                               hex(id(self)))

    @Attribute  # Lazy-evaluation of reading procedure
    def reader(self):
        """ Responsible for parsing the .cfg file into a list of key, value pairs

        :rtype: collections.Sequence[tuple]
        """
        cfg = config.SafeConfigParser()
        cfg.read(os.path.abspath(os.path.join(self.__default_directory__, self.filename)))
        entries = []
        for section in cfg.sections():
            entries += cfg.items(section)
        return dict(entries)

    @Attribute
    def corrected_mass_flow(self):
        """ Correct mass flow in SI kilogram per second  """
        return float(self.reader['corrected_mass_flow'])

    @Attribute
    def nozzle_type(self):
        """ Defines the geometry of the exit nozzle """
        return self.reader['nozzle_type']

    @Attribute
    def bypass_ratio(self):
        """ Ratio of cold-nozzle mass flow to core mass flow """
        return float(self.reader['bypass_ratio'])

    @Attribute
    def combustion_temperature(self):
        """ Temperature of outflow from the combustion chamber in SI Kelvin [k] """
        return float(self.reader['combustion_temperature'])

    @Attribute
    def pr_cc(self):
        """ Pressure Ratio across the Combustion Chamber """
        return float(self.reader['pr_cc'])

    @Attribute
    def pr_fan(self):
        """ Pressure Ratio across the Fan"""
        return float(self.reader['pr_fan'])

    @Attribute
    def pr_lpc(self):
        """ Pressure Ratio across the Low-Pressure Compressor """
        return float(self.reader['pr_lpc'])

    @Attribute
    def pr_hpc(self):
        """ Pressure Ratio across the High-Pressure Compressor """
        return float(self.reader['pr_hpc'])

    @Attribute
    def eta_fan(self):
        """ Fan Isentropic Efficiency """
        return float(self.reader['eta_fan'])

    @Attribute
    def eta_lpc(self):
        """ Low-Pressure Compressor Efficiency """
        return float(self.reader['eta_lpc'])

    @Attribute
    def eta_hpc(self):
        """ High-Pressure Compressor Efficiency """
        return float(self.reader['eta_hpc'])

    @Attribute
    def eta_lpt(self):
        """ Low-Pressure Turbine Efficiency """
        return float(self.reader['eta_lpt'])

    @Attribute
    def eta_hpt(self):
        """ High-Pressure Turbine Efficiency """
        return float(self.reader['eta_hpt'])

    @Attribute
    def eta_mech(self):
        """ Mechanical Efficiency """
        return float(self.reader['eta_mech'])

    @Attribute
    def eta_cc(self):
        """ Combustion Efficiency """
        return float(self.reader['eta_cc'])

    @Attribute
    def eta_nozzle(self):
        """ (Exit) Nozzle Isentropic Efficiency """
        return float(self.reader['eta_nozzle'])

    @Attribute
    def eta_inlet(self):
        """ Inlet Isentropic Efficiency """
        return float(self.reader['eta_inlet'])


if __name__ == '__main__':
    obj = SpecParser()
    print(obj.eta_inlet)

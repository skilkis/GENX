#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Contains all abstract class definitions  """

from base import Base
from utils import Attribute, Unassigned

__author__ = 'San Kilkis'


class FlowCondition(Base):

    # Providing dummy attributes for the debugger, these are partially overwritten at run-time by the Attributes below
    mass_flow = Unassigned('mass_flow')
    mach = Unassigned('mach')
    t_static = Unassigned('t_static')
    t_total = Unassigned('t_total')
    p_static = Unassigned('p_static')
    p_total = Unassigned('p_total')
    medium = Unassigned('medium')

    def __init__(self, **kwargs):
        """

        :param float mass_flow:
        :param float mach:
        :param float t_static:
        :param float p_static:
        :param str medium:
        :param float t_total:
        :param float p_total:
        """
        for key, value in zip(kwargs.keys(), kwargs.values()):
            command = 'self.{} = {}'.format(key, "'{}'".format(value) if type(value) is str else value)
            exec command

    @Attribute
    def kappa(self):
        """ Specific Heat of the Selected Medium at Constant Pressure c_p in SI Joule per kilogram Kelvin[J/kg K] """
        if self.medium == 'air':
            return self.kappa_air
        elif self.medium == 'gas':
            return self.kappa_gas
        else:
            raise AttributeError("Data for the provided medium '{}' does not exist".format(self.medium))

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

    @staticmethod
    def assert_float(entry):
        return float(entry) if entry is not None or str else entry


if __name__ == '__main__':
    obj = FlowCondition(t_static=216., medium='air')
    print(obj.t_total)

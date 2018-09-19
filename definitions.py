#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Contains all abstract class definitions  """

from base import Base
from utils import Attribute

__author__ = 'San Kilkis'


class FlowCondition(Base):

    def __init__(self, **kwargs):
        """

        :param float mass_flow:
        :param float mach:
        :param float t_static:
        :param float p_static:
        :param str medium:
        """
        for key, value in zip(kwargs.keys(), kwargs.values()):
            self.key = value
        # self.mass_flow = self.assert_float(mass_flow)
        # self.mach = self.assert_float(mach)
        # self.t_static = self.assert_float(t_static)
        # self.p_static = self.assert_float(p_static)
        # self.medium = medium

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
        return self.t_static * (1 + (((self.kappa - 1) / 2.) * self.mach**2))

    @Attribute
    def p_total(self):
        return self.p_static * ((1 + (((self.kappa - 1) / 2.) * self.mach**2))**(self.kappa / (self.kappa - 1)))

    @staticmethod
    def assert_float(entry):
        return float(entry) if entry is not None or str else entry


if __name__ == '__main__':
    obj = FlowCondition(mach=0.8, t_static=216., p_static=22632, medium='air')
    print(obj.t_total)
    # print(obj.p_total)

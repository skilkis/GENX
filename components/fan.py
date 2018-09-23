#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ADD DOC """

from definitions import Stage, FlowCondition
from inlet import Inlet
from compressor import Compressor

__author__ = 'San Kilkis'

# TODO add function for plotting line on TS diagram


class Fan(Compressor):
    """ A fan is more or less a compressor thus the total temperature and pressure attributes are from
    :py:class:`Compressor`"""

    def __init__(self, inflow, eta, pressure_ratio, station_number):
        """

        :param inflow:
        :param eta:
        :param pressure_ratio: Pressure Ratio
        """
        super(Fan, self).__init__(inflow, eta, pressure_ratio, station_number)

    @property
    def outflow(self):
        return FlowCondition(mass_flow=self.inflow.mass_flow,
                             t_total=self.t_total,
                             p_total=self.p_total,
                             medium='air',
                             station_number='21')


if __name__ == '__main__':
    ambient_conditions = FlowCondition(corrected_mass_flow=1400.,
                                       mach=0.8, t_static=216, p_static=22632, station_number='1', medium='air')
    inlet = Inlet(ambient=ambient_conditions, eta=0.98)
    obj = Fan(inflow=inlet.outflow, eta=0.92, pressure_ratio=1.6, station_number='2')
    print(obj.t_total)
    print(obj.p_total)

    # print(obj.p_total)
    # print(obj.t_total)

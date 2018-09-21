#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ADD DOC """

from definitions import Stage, FlowCondition
from collections import Iterable

__author__ = 'San Kilkis'

# TODO add function for plotting line on TS diagram


class Spool(Stage):

    def __init__(self, compressor_in, eta):
        """

        :param Compressor or collections.Sequence[Compressor] compressor_in:
        :param float eta:
        """
        self.compressor_in = compressor_in
        self.eta = eta

    @property
    def work_required(self):
        try:
            if isinstance(self.compressor_in, Iterable):
                total_work = sum([component.work_done for component in self.compressor_in])
                return total_work / self.eta
            else:
                return self.compressor_in.work_done / self.eta
        except AttributeError as e:
            raise e


if __name__ == '__main__':
    from inlet import Inlet
    from fan import Fan
    from bypass import Bypass
    from compressor import Compressor
    ambient_conditions = FlowCondition(corrected_mass_flow=1400.,
                                       mach=0.8, t_static=216, p_static=22632, station_number='1', medium='air')
    inlet = Inlet(inflow=ambient_conditions, eta=0.98)
    fan = Fan(inflow=inlet.outflow, eta=0.92, pressure_ratio=1.6, station_number='21')
    bypass = Bypass(inflow=fan.outflow, bypass_ratio=8.)
    lpc = Compressor(inflow=bypass.outflow_core, eta=0.9, pressure_ratio=1.4, station_number='25')
    hpc = Compressor(inflow=lpc.outflow, eta=0.9, pressure_ratio=19, station_number='3')
    lp_spool = Spool(compressor_in=(fan, lpc), eta=0.99)
    print(lp_spool.work_required)
    print(lpc.work_done)
    print(hpc.inflow.mass_flow)
    print(hpc.inflow.t_total)
    print(hpc.p_total)
    print(hpc.t_total)
    print(hpc.work_done)

    # print(obj.p_total)
    # print(obj.t_total)

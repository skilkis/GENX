#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ADD DOC """

from definitions import Stage, FlowCondition

__author__ = 'San Kilkis'

# TODO add function for plotting line on TS diagram


class CombustionChamber(Stage):

    def __init__(self, inflow, eta, pressure_ratio, t_total_exit):
        """

        :param inflow:
        :param eta:
        :param pressure_ratio: Pressure Ratio
        """
        self.inflow = inflow
        self.eta = eta
        self.pressure_ratio = pressure_ratio
        self.t_total_exit = t_total_exit

    @property
    def fuel_flow(self):
        """ Fuel flow in the Combustion Chamber in SI kilogram per second [kg s^-1] """
        return (self.inflow.mass_flow * self.specific_heat_gas * (self.t_total_exit - self.inflow.t_total)) /\
               (self.eta * self.lower_heating_value)

    @property
    def p_total(self):
        """ Total pressure changes proportionally across the combustion chamber as a multiple of the pressure ratio """
        return self.inflow.p_total * self.pressure_ratio

    @property
    def outflow(self):
        return FlowCondition(mass_flow=self.inflow.mass_flow + self.fuel_flow,
                             t_total=self.t_total_exit,
                             p_total=self.p_total,
                             medium='gas',
                             station_number='4')


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
    combustor = CombustionChamber(inflow=hpc.outflow, eta=0.99, pressure_ratio=0.96, t_total_exit=1450.)
    print(fan.work_done)
    print(hpc.outflow.t_total)
    print(combustor.outflow.mass_flow)
    print(combustor.outflow.p_total)
    print(combustor.fuel_flow)

    # print(obj.p_total)
    # print(obj.t_total)

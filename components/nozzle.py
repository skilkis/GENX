#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ADD DOC """

from definitions import Stage, FlowCondition
from collections import Iterable
import numpy as np

__author__ = 'San Kilkis'

# TODO add function for plotting line on TS diagram


class Nozzle(Stage):

    # TODO finish documentation
    def __init__(self, inflow, ambient, eta, nozzle_type, station_number):
        """ TEST LALALAL

        :param FlowCondition inflow: Flow conditions entering the nozzle
        :param FlowCondition ambient: Ambient flow conditions
        :param eta: Nozzle efficiency
        :param str nozzle_type: Specifies the geometry of the nozzle
        :param collections.Sequence[str, str] station_number: Station number before and after the nozzle throat
        """

        self.inflow = inflow
        self.ambient = ambient
        self.eta = eta
        self.station_number = station_number

        # Filtering nozzle type
        if nozzle_type == 'convergent':
            self.nozzle_type = nozzle_type
        else:
            if nozzle_type is None:
                self.nozzle_type = 'convergent'
            else:
                raise ValueError('Only convergent nozzles are currently supported')

    @property
    def p_critical(self):
        """ Critical Pressure at which the :py:class:`Nozzle` is choked in SI Pascal [Pa] """
        return ((1 - ((1 / self.eta) * ((self.inflow.kappa - 1) / (self.inflow.kappa + 1)))) **
                (self.inflow.kappa / (self.inflow.kappa - 1))) * self.p_total

    @property
    def critical_ratio(self):
        """ Pressure ratio w.r.t. the critical pressure """
        return self.p_total / self.p_critical

    @property
    def choked(self):
        """ Boolean switch case that returns ``True`` if the flow is chocked else ``False`` """
        # TODO use isintance(self.p_total, Iterable) and create a new conditional that checks each entry in vector

        @np.vectorize
        def check(p_total, p_critical):
            if p_total > p_critical:
                # print('{}: Nozzle is choked! Total pressure {} [Pa]'
                #       ' exceeds critical pressure of {} [Pa]'.format(self, self.p_total, self.p_critical))
                return True
            else:
                raise ValueError('Nozzle is not choked thus the mach number at the exit is not known,'
                                 ' stopping calculation')

        return check(self.p_total, self.p_critical)

    @property
    def t_total(self):
        """ Total temperature at the end of the py:class:`Nozzle` right before the throat n SI Kelvin [K]. The total
        temperature in the nozzle remains constant.

        :rtype: float
        """
        return self.inflow.t_total

    @property
    def t_exit(self):
        """ Static temperature at the exit of the py:class:`Nozzle` after the throat n SI Kelvin [K].

        :rtype: float
        """
        return self.t_total * (2. / (self.inflow.kappa + 1.))

    @property
    def p_total(self):
        """ Total pressure at the end of the py:class:`Nozzle` right before the throat in SI Kelvin [K]. The total
        temperature in the nozzle remains constant.

        :rtype: float
        """
        return self.inflow.p_total

    @property
    def p_exit(self):
        """ Static temperature at the exit of the py:class:`Nozzle` after the throat n SI Kelvin [K].

        :rtype: float
        """
        return self.p_total / self.critical_ratio

    @property
    def throat_area(self):
        """ Cross-sectional area of the nozzle throat in SI meter squared [m^2]

        :rtype: float
        """
        return self.outflow.mass_flow / (self.outflow.rho * self.outflow.velocity)

    @property
    def momentum_thrust(self):
        """ Thrust produced by the nozzle due to the momentum difference between the jet velocity and the ambient
        velocity in SI Newton [N]

        :rtype float
        """
        return self.outflow.mass_flow * (self.outflow.velocity - self.ambient.velocity)

    @property
    def pressure_thrust(self):
        """ Thrust produced due to the difference in static pressure between the nozzle exit and ambient conditions in
        SI Newton [N]

        :rtype: float
        """
        return self.throat_area * (self.outflow.p_static - self.ambient.p_static)

    @property
    def thrust(self):
        """ Total thrust produced by the nozzle in SI Newton [N]

        :rtype: float
        """
        return self.momentum_thrust + self.pressure_thrust

    @property
    def nozzle_flow(self):
        """ Represents the flow conditions in the nozzle before the throat """
        return FlowCondition(mass_flow=self.inflow.mass_flow,
                             t_total=self.t_total,
                             p_total=self.p_total,
                             medium=self.inflow.medium,
                             station_number=self.station_number[0])

    @property
    def outflow(self):
        """ Represents the flow conditions after the nozzle throat """
        return FlowCondition(mass_flow=self.inflow.mass_flow,
                             mach=1. if self.choked.any() else None,
                             t_static=self.t_exit,
                             p_static=self.p_exit,
                             medium=self.inflow.medium,
                             station_number=self.station_number[1])


if __name__ == '__main__':
    from inlet import Inlet
    from fan import Fan
    from bypass import Bypass
    from compressor import Compressor
    from combustion import CombustionChamber
    from spool import Spool
    from turbine import Turbine
    ambient_conditions = FlowCondition(corrected_mass_flow=1400.,
                                       mach=0.8, t_static=216., p_static=22632., station_number='1', medium='air')
    inlet = Inlet(ambient=ambient_conditions, eta=0.98)
    fan = Fan(inflow=inlet.outflow, eta=0.92, pressure_ratio=1.6, station_number='21')
    bypass = Bypass(inflow=fan.outflow, bypass_ratio=8.)
    lpc = Compressor(inflow=bypass.outflow_core, eta=0.9, pressure_ratio=1.4, station_number='25')
    hpc = Compressor(inflow=lpc.outflow, eta=0.9, pressure_ratio=19, station_number='3')
    combustor = CombustionChamber(inflow=hpc.outflow, eta=0.99, pressure_ratio=0.96, t_total_exit=1450.)
    lp_spool = Spool(compressor_in=(fan, lpc), eta=0.99)
    hp_spool = Spool(compressor_in=hpc, eta=0.99)
    hpt = Turbine(inflow=combustor.outflow, spool_in=hp_spool, eta=0.92, station_number='45')
    lpt = Turbine(inflow=hpt.outflow, spool_in=lp_spool, eta=0.92, station_number='5')
    nozzle_core = Nozzle(inflow=lpt.outflow, ambient=ambient_conditions, eta=0.98,
                         nozzle_type='convergent', station_number=('7', '8'))
    nozzle_bypass = Nozzle(inflow=bypass.outflow_bypass, ambient=ambient_conditions, eta=0.98,
                           nozzle_type='convergent', station_number=('16', '18'))
    print(nozzle_core.p_critical)
    print(nozzle_core.choked)
    print(nozzle_core.pressure_thrust)


    # print(obj.p_total)
    # print(obj.t_total)

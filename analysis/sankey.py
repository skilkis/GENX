#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Contains all abstract class definitions  """

from components import Turbine
from collections import namedtuple
from utils import Attribute

__author__ = 'San Kilkis'

# TODO Make a simple SankeyDiagram with matplotib


class SankeyDiagram(object):

    def __init__(self, engine_in=None):
        """ Analyzes an engine for various losses and efficiencies passed through :py:attr:`engine_in`.

        :param Engine engine_in:
        """

        self.engine_in = engine_in

    @Attribute
    def chemical_power(self):
        """ Obtains the total chemical power available in the kerosene in SI Watt [W}

        :rtype: float
        """
        cc = self.engine_in.combustor
        return cc.fuel_flow * cc.lower_heating_value

    @Attribute
    def heat_power(self):
        cc = self.engine_in.combustor  # Localizing combustion chamber for clarity
        return cc.inflow.mass_flow * cc.outflow.specific_heat * (cc.outflow.t_total - cc.inflow.t_total)

    @Attribute
    def turbine_power(self):
        """ Obtains the total power output of all :py:class:`Turbine` through a summing operation in SI Watt [W]

        :rtype: float
        """
        return sum([turbine.work_output for turbine in self.engine_in.get_children(Turbine)])

    @Attribute
    def bypass_power(self):
        """ Obtains the power output of the bypass nozzle in SI Watt [W]

        :rtype: float
        """
        nb = self.engine_in.nozzle_bypass  # Localizing the bypass nozzle for readability
        return nb.inflow.mass_flow * nb.inflow.specific_heat * (nb.inflow.t_total - nb.outflow.t_static)

    @Attribute
    def core_power(self):
        """ Obtains the power output of the cold nozzle in SI Watt [W]

        :rtype: float
        """
        nc = self.engine_in.nozzle_core  # Localizing the bypass nozzle for readability
        return nc.inflow.mass_flow * nc.inflow.specific_heat * (nc.inflow.t_total - nc.outflow.t_static)

    @Attribute
    def temperature_g(self):
        """ """
        cc = self.engine_in.combustor
        t_4, m_c, cp_g = cc.outflow.t_total, cc.outflow.mass_flow, cc.outflow.specific_heat
        fan_bypass_work = self.engine_in.nozzle_bypass.inflow.mass_flow * self.engine_in.nozzle_bypass.inflow.specific_heat * (self.engine_in.fan.outflow.t_total - self.engine_in.fan.inflow.t_total)
        print(fan_bypass_work)
        return t_4 - ((self.turbine_power - fan_bypass_work) / (m_c * cp_g))

    @Attribute
    def pressure_g(self):
        lpt = self.engine_in.lpt
        t_4 = self.engine_in.combustor.outflow.t_total
        p_4 = self.engine_in.combustor.outflow.p_total
        return p_4 * (1 - (1/self.engine_in.eta_lpt) *
                      (1 - (lpt.outflow.t_total / t_4))) ** (lpt.inflow.kappa_gas / (lpt.inflow.kappa_gas - 1.))

    # TODO make this more general
    @Attribute
    def equivalent_velocity(self):
        """ Computes the equivalent velocity that would be obtained after expansion downstream of the nozzle in
        SI meter per second [m/s]

        :rtype: float
        """
        nc, nb, v_0 = self.engine_in.nozzle_core, self.engine_in.nozzle_bypass, self.engine_in.ambient.velocity
        v_c, v_b = nc.thrust / nc.outflow.mass_flow + v_0, nb.thrust / nb.outflow.mass_flow + v_0
        velocity = namedtuple('EquivalentVelocity', ('core', 'bypass'))
        return velocity(v_c, v_b)

    @Attribute
    def momentum_power(self):
        nc, nb, v_0 = self.engine_in.nozzle_core, self.engine_in.nozzle_bypass, self.engine_in.ambient.velocity
        return 0.5 * (nc.outflow.mass_flow * (nc.outflow.velocity ** 2 - v_0 ** 2)
                      + nb.outflow.mass_flow * (nb.outflow.velocity ** 2 - v_0 ** 2))

    # TODO make this more general
    @Attribute
    def pressure_power(self):
        """ Calculates the power generated by the nozzles """
        nc, nb, p_s = self.engine_in.nozzle_core, self.engine_in.nozzle_bypass, self.engine_in.ambient.p_static
        return (nc.throat_area * (nc.outflow.p_static - p_s) * nc.outflow.velocity +
                nb.throat_area * (nb.outflow.p_static - p_s) * nb.outflow.velocity)

    @Attribute
    def jet_power(self):
        """ Propulsive jet power in SI Watt [W]

        :rtype: float
        """
        return self.momentum_power + self.pressure_power
    #
    # @Attribute
    # def jet_power(self):
    #     """ Propulsive jet power in SI Watt [W]
    #
    #     :rtype: float
    #     """
    #     v_c, v_b, v_0 = self.equivalent_velocity.core, self.equivalent_velocity.bypass, self.engine_in.ambient.velocity
    #     nc, nb, = self.engine_in.nozzle_core, self.engine_in.nozzle_bypass
    #
    #     # return 0.5 * (nc.outflow.mass_flow * (v_c ** 2 - v_0 ** 2) + nb.outflow.mass_flow * (v_b ** 2 - v_0 ** 2))
    #     return 0.5 * (nc.outflow.mass_flow * (v_c ** 2 - v_0 ** 2) + nb.outflow.mass_flow * (v_b ** 2 - v_0 ** 2))

    @Attribute
    def thrust_power(self):
        """ Calculates the power utilizing the total thrust force and multiplies it by the ambient velocity.
        This results in a so-called Thrust Power in SI Watt [W]

        :rtype: float
        """
        return self.engine_in.thrust * self.engine_in.ambient.velocity

    @Attribute
    def thrust_power_2(self):
        return (self.engine_in.nozzle_core.outflow.mass_flow * (self.equivalent_velocity.core - self.engine_in.ambient.velocity) + \
               self.engine_in.nozzle_bypass.outflow.mass_flow * (
                           self.equivalent_velocity.bypass - self.engine_in.ambient.velocity)) * self.engine_in.ambient.velocity



    # @Attribute
    # def pressure_g(self):
    #     hpt = self.engine_in.hpt
    #     return hpt.inflow.p_total * ((hpt.outflow.t_total/hpt.inflow.t_total) ** (hpt.inflow.specific_heat/ (self.engine_in.eta_cc * (hpt.inflow.specific_heat - 1.))))

    @Attribute
    def gas_power(self):
        eng = self.engine_in
        m_dot = eng.combustor.outflow.mass_flow
        cp_g = eng.combustor.outflow.specific_heat
        t_total_g = eng.lpt.outflow.t_total
        p_g = self.pressure_g
        p_0 = self.engine_in.ambient.p_total

        return m_dot * cp_g * t_total_g * (1. - (p_0 / p_g)**((cp_g - 1.)/cp_g)) - (0.5 * self.engine_in.bypass.mass_flow_core * self.engine_in.ambient.velocity ** 2)

    @Attribute
    def eta_prop(self):
        """ Combined propulsive efficiency of all nozzles present in the engine. This represents the efficiency
        between the useful work output (thrust) and the total work output of the nozzle which is the jet power.

        :rtype: float
        """
        return self.thrust_power / self.jet_power

    @Attribute
    def eta_ideal(self):
        """ Calculates the Ideal Cycle Thermodynamic Efficiency (from Lecture 2. Slide 20)

        :return:
        """
        return 1. - (1. / (self.engine_in.pr_ovr ** ((self.engine_in.ambient.kappa_air - 1.) /
                                                     self.engine_in.ambient.kappa_air)))

    @Attribute
    def eta_carnot(self):
        """ Carnot Cycle Thermal Efficiency (max. possible efficiency) calculated from the ratio between the ambient
        total temperature and the combustion chamber exit total temperature.

        :rtype: float
        """
        return 1 - (self.engine_in.inlet.outflow.t_total / self.engine_in.combustor.outflow.t_total)

    # @Attribute
    # def gas_power(self):
    #     eng = self.engine_in
    #     m_dot = eng.combustor.outflow.mass_flow
    #     cp_g = eng.combustor.outflow.specific_heat
    #     cp_a = self.engine_in.nozzle_bypass.inflow.specific_heat
    #     t_total_g = eng.lpt.outflow.t_total
    #     p_g = self.engine_in.lpt.outflow.p_total
    #     p_a = self.engine_in.nozzle_bypass.inflow.p_total
    #     p_0 = self.engine_in.ambient.p_total
    #
    #     return self.engine_in.bypass.mass_flow_bypass * cp_a * self.engine_in.nozzle_bypass.inflow.t_total * (1. - (p_0 / p_a)**((cp_a - 1.)/cp_a)) + m_dot * cp_g * t_total_g * (1. - (p_0 / p_g)**((cp_g - 1.)/cp_g)) - (0.5 * self.engine_in.ambient.mass_flow * self.engine_in.ambient.velocity ** 2)

    def plot(self):
        return NotImplementedError('Plotting of the Sankey Diagram is not yet implemented, this is planned for a'
                                   'future release')


if __name__ == '__main__':
    from engine import Engine
    obj = SankeyDiagram(engine_in=Engine(filename='GENX.cfg', ideal_cycle=True))
    # print(obj.turbine_power/obj.turbine_power2)
    # print(obj.engine_in.ambient.p_total)
    # print(obj.heat_power/obj.chemical_power)
    # print(obj.engine_in.ambient.mass_flow)
    print(obj.pressure_g/obj.engine_in.lpt.outflow.p_total)
    # # print(obj.turbine_power)
    print('Total Pressure Gas Generator: {} [Pa]'.format(obj.pressure_g))
    print('Bypass Power: {} [W]'.format(obj.bypass_power))
    print('Gas Power: {} [W]'.format(obj.gas_power))
    print('Turbine Power: {} [W]'.format(obj.turbine_power))
    print('Thermodynamic (Gas Power) Efficiency: {}'.format(obj.gas_power/obj.heat_power))
    print('Jet Power: {} [W]'.format(obj.jet_power))
    print('Thermal Efficiency: {}'.format(obj.jet_power/obj.chemical_power))
    print('Carnot Efficiency: {}'.format(obj.eta_carnot))
    print('Ideal Thermal Efficiency: {}'.format(obj.eta_ideal))
    print('Overall Pressure Ratio: {}'.format(obj.engine_in.pr_ovr))
    print('Jet Propulsive Efficiency: {}'.format(obj.jet_power / obj.gas_power))
    print('Propulsive Efficiency: {}'.format(obj.eta_prop))
    print('Total Efficiency: {}'.format(obj.thrust_power / obj.chemical_power))
    # print(obj.bypass_power + obj.gas_power)
    print('Gas Generator Temperature: {} [K]'.format(obj.temperature_g))
    # print(obj.engine_in.lpt.outflow.t_total)
    # print(obj.engine_in.lpt.outflow.station_number)
    # obj.engine_in.calculate_cycle()
    # print(obj.gas_power)
    print(obj.thrust_power, obj.thrust_power_2)

    # DIFFERENCE IN P_GG vs IDEAL P_GG IS DUE TO CHOKING, GAS POWER BEFORE NOZZLE IS ALTERED BY CHOKING CONDITION,
    # CANNOT USE STATIC PRESSURE TO GAIN UNDERSTANDING INTO THE FLOW PROPERTIES BEFORE THE CHOKE (INFORMATION IS
    # ONLY 1 WAY)

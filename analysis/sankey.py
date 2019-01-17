#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Contains all abstract class definitions  """

from components import Turbine
from collections import namedtuple
from utils import Attribute
from directories import DIRS
import os

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
        """ Obtains the actual power output of the comustion chamber in SI Watt [W}

        :rtype: float
        """
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
        """ Obtains the power output of the bypass fan to the bypassed air flow in SI Watt [W]

        :rtype: float
        """
        fan, nb = self.engine_in.fan, self.engine_in.nozzle_bypass  # Localizing variables for readability
        return nb.inflow.mass_flow * nb.inflow.specific_heat * (fan.outflow.t_total - fan.inflow.t_total)

    @Attribute
    def temperature_g(self):
        """ Calculates the total temperature that would theoretically be achieved if the LPT would not be driving
        a fan which is exerting power into a bypassed section in SI Kelvin [K]

        :rtype: float
        """
        cc, hpt = self.engine_in.combustor, self.engine_in.hpt
        t_45, m_c, cp_g = hpt.outflow.t_total, cc.outflow.mass_flow, cc.outflow.specific_heat
        return t_45 - ((self.engine_in.lpt.work_output - self.bypass_power) / (m_c * cp_g))

    @Attribute
    def pressure_g(self):
        """ Calculates the corresponding total pressure in SI Pascal [Pa] at the theoretical condition where the LPT
        would only serve to drive a booster + fan combination that only compresses core air flow

        :rtype: float
        """
        hpt = self.engine_in.hpt
        t_45 = hpt.outflow.t_total
        p_45 = hpt.outflow.p_total
        return p_45 * ((1 - (1/self.engine_in.eta_hpt) *
                       (1 - (self.temperature_g / t_45))) ** (hpt.inflow.kappa_gas / (hpt.inflow.kappa_gas - 1.)))

    @Attribute
    def gas_power(self):
        """ Computes the theoretical power remaining in the core flow after work extraction by the Turbines in
        SI Watt [W]. In reality, this is done to be able to compare the efficiencies of a bypassed engine with that of
        a regular turbojet. In the latter case the turbine(s) exert work only on the core flow, thus the remaining
        power in the core flow is simply that which is not extracted by the turbine. However, in the turbofan, part of
        the work extracted by the turbine is used for the bypassed air, thus without utilizing this theoretical value,
        the bypassed engine would already be at a disadvantage in Thermodynamic efficiency since it would seem that
        the work going to drive the fan

        :rtype: float
        """
        eng = self.engine_in
        m_dot, cp_g, = eng.combustor.outflow.mass_flow, eng.combustor.outflow.specific_heat
        kappa_gas = eng.combustor.outflow.kappa_gas
        t_total_g = self.temperature_g
        p_g = self.pressure_g
        p_0 = self.engine_in.ambient.p_total

        return m_dot * cp_g * t_total_g * (1. - (p_0 / p_g)**((kappa_gas - 1.)/kappa_gas)
                                           ) - (0.5 * self.engine_in.bypass.mass_flow_core *
                                                self.engine_in.ambient.velocity ** 2)

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
        """ Calculates the power generated by the nozzles due to pressure thrust """
        nc, nb, p_s = self.engine_in.nozzle_core, self.engine_in.nozzle_bypass, self.engine_in.ambient.p_static
        return (nc.throat_area * (nc.outflow.p_static - p_s) * nc.outflow.velocity +
                nb.throat_area * (nb.outflow.p_static - p_s) * nb.outflow.velocity)

    @Attribute
    def prop_power(self):
        """ Propulsive power in SI Watt [W]. This quantity represents the increase in kinetic power of the air/gas.
        P_prop is the symbol in the reader.

        :rtype: float
        """
        return self.momentum_power + self.pressure_power

    @Attribute
    def prop_power_effective(self):
        """ Propulsive power calculated with the effective velocity in SI Watt [W]. At the moment this is the used value
        however it results in efficiencies larger than 1.0.

        :rtype: float
        """
        v_c, v_b, v_0 = self.equivalent_velocity.core, self.equivalent_velocity.bypass, self.engine_in.ambient.velocity
        nc, nb, = self.engine_in.nozzle_core, self.engine_in.nozzle_bypass

        return 0.5 * (nc.outflow.mass_flow * (v_c ** 2 - v_0 ** 2) + nb.outflow.mass_flow * (v_b ** 2 - v_0 ** 2))

    @Attribute
    def thrust_power(self):
        """ Calculates the power utilizing the total thrust force and multiplies it by the ambient velocity.
        This results in a so-called Thrust Power in SI Watt [W]

        :rtype: float
        """
        return self.engine_in.thrust * self.engine_in.ambient.velocity

    @Attribute
    def eta_comb(self):
        """ Calculates the combustion efficiency of the engine.

        :rtype: float
        """
        return self.heat_power / self.chemical_power

    @Attribute
    def eta_thdy(self):
        """ Calculates the thermodynamic efficiency of the engine. This represents the ratio between the total potential
        power that can be transformed into useful work and the power available after the combustion process.

        :rtype: float
        """
        return self.gas_power / self.heat_power

    @Attribute
    def eta_thm(self):
        """ Calculates the thermal energy of the cycle which relates the propulsive power

        :rtype: float
        """
        return self.prop_power / self.chemical_power

    @Attribute
    def eta_jet(self):
        """ Calculates the jet generation efficiency (pg. 77 of Reader).


        :rtype: float
        """
        return self.prop_power / self.gas_power

    @Attribute
    def eta_prop(self):
        """ Calculates the propulsive efficiency (Froude Efficiency) which relates the power in the flow that has been
        transformed into useful work to the total chemical power in the kerosene.

        :rtype: float
        """
        return self.thrust_power / self.prop_power

    @Attribute
    def eta_total(self):
        """ Calculates the total efficiency of the cycle which relates the useful work that has been done to the flow to
        achieve thrust to the total chemical power in the kerosene.

        :rtype: float
        """
        return self.thrust_power / self.chemical_power

    @Attribute
    def eta_ideal(self):
        """ Calculates the Ideal Cycle Thermodynamic Efficiency (from Lecture 2. Slide 20)

        :return:
        """
        return 1. - (self.engine_in.pr_ovr ** ((1 - self.engine_in.ambient.kappa_air ) /
                                                     self.engine_in.ambient.kappa_air))

    @Attribute
    def eta_carnot(self):
        """ Carnot Cycle Thermal Efficiency (max. possible efficiency, pg. 24 of reader) calculated from the ratio
        between the ambient total temperature and the combustion chamber exit total temperature.

        :rtype: float
        """
        return 1 - (self.engine_in.inlet.outflow.t_total / self.engine_in.combustor.outflow.t_total)

    @Attribute
    def sankey_powers(self):
        """ Creates a dictionary of powers used for creating the Sankey Diagram, these can be viewed on
        S18 of Lecture 2. All values are in SI Mega Watt [MW] for readability.

        :rtype: dict
        """
        return {'chemical_power':  self.chemical_power / 1e6,
                'heat_power': self.heat_power / 1e6,
                'gas_power': self.gas_power / 1e6,
                'prop_power': self.prop_power / 1e6,
                'thrust_power': self.thrust_power / 1e6}

    @Attribute
    def sankey_etas(self):
        """ Creates a dictionary of power remaining ratios (loosely an efficiency as compared to the total chemical
        power) used for creating the Sankey Diagram, these can be viewed on S18 of Lecture 2

        :rtype: dict
        """
        eta_dict = {}
        for key, value in self.sankey_powers.items():
            eta_dict[key.split('_')[0] + '_eta'] = value / (self.chemical_power / 1e6)
        return eta_dict

    @Attribute
    def sankey_losses(self):
        """ Creates a dictionary of loss ratios used for creating the Sankey Diagram, these can be viewed on
        S18 of Lecture 2

        :rtype: dict
        """
        return {'incomplete_combustion':  (self.chemical_power - self.heat_power) / self.chemical_power,
                'heat': (self.heat_power - self.gas_power) / self.chemical_power,
                'heat_jet': (self.gas_power - self.prop_power) / self.chemical_power,
                'kinetic_energy': (self.prop_power - self.thrust_power) / self.chemical_power}

    def write_csv(self):
        """ Writes an output .csv file containing relevant parameters to create the Sankey Diagram """
        # Second pass writes ordered .csv file
        engine_name = self.engine_in.__name__
        filename = '{}_sankey_{}.csv'.format(engine_name, 'ideal' if self.engine_in.ideal_cycle else 'real')
        with open(os.path.join(DIRS['CSV_DIR'], filename), "w") as csv:
            csv.write('<<< Powers >>>\n')
            for key, value in self.sankey_powers.items():
                csv.write('{}\t{}\n'.format(key, value))

            csv.write('\n<<< Efficiencies >>>\n')
            for key, value in self.sankey_etas.items():
                csv.write('{}\t{}\n'.format(key, value))

            csv.write('\n<<< Losses >>>\n')
            for key, value in self.sankey_losses.items():
                csv.write('{}\t{}\n'.format(key, value))

    def plot(self):
        return NotImplementedError('Plotting of the Sankey Diagram is not yet implemented, this is planned for a'
                                   'future release')


if __name__ == '__main__':
    from engine import Engine
    obj = SankeyDiagram(engine_in=Engine(filename='GE90.cfg', ideal_cycle=True))
    print('Gas Generator Temperature: {} [K]'.format(obj.temperature_g))
    print('Total Pressure Gas Generator: {} [Pa]'.format(obj.pressure_g))
    print('Chemical Power: {} [W]'.format(obj.chemical_power))
    print('Heat Power: {} [W]'.format(obj.heat_power))
    print('Bypass Power: {} [W]'.format(obj.bypass_power))
    print('Gas Power: {} [W]'.format(obj.gas_power))
    print('Jet Power: {} [W]'.format(obj.prop_power))
    print('Thrust Power: {} [W]'.format(obj.thrust_power))
    print('Combustion Efficiency: {}'.format(obj.eta_comb))
    print('Thermodynamic (Gas Power) Efficiency: {}'.format(obj.eta_thdy))
    print('Thermal Efficiency: {}'.format(obj.eta_thm))
    print('Jet Propulsive Efficiency: {}'.format(obj.eta_jet))
    print('Propulsive Efficiency: {}'.format(obj.eta_prop))
    print('Total Efficiency: {}'.format(obj.eta_total))
    print('Ideal Thermal Efficiency: {}'.format(obj.eta_ideal))
    print('Carnot Efficiency: {}'.format(obj.eta_carnot))
    # print('Total Efficiency: {}'.format(obj.eta_comb * obj.eta_thdy * obj.eta_jet * obj.eta_prop)) # Double Check!
    # obj.engine_in.calculate_cycle()
    # obj.write_csv()

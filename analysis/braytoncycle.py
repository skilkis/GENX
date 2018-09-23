#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Contains all abstract class definitions  """

from engine import Engine
from components import Inlet
import numpy as np
import matplotlib.pyplot as plt
import requests
from utils import ProgressBar, Attribute
from math import log

__author__ = 'San Kilkis'


class BraytonCycle(object):

    def __init__(self, engine_in=Engine()):
        self.engine_in = engine_in

    @Attribute
    def specific_entropy(self):
        """ Allows look-up of reference Specific Entropy `s` of the ambient flow depending on the ambient static
        temperature :pr:attr:`engine_in.ambient.t_static` and ambient static pressure
        `py:attr:`engine_in.ambient.p_static`. If a cached value is already present in the look-up table then the online
        calculator won't be accessed. Otherwise, this process takes some time as a request to the server has to be made.

        :return: Specific Entropy in SI Joule per kilogram Kelvin [J/kg K]
        :rtype: float
        """
        prog = ProgressBar('Fetching Entropy Value', threaded=True)
        temp = self.engine_in.ambient.t_static - 273.15
        pres = self.engine_in.ambient.p_static / 1000.
        tol = {'temperature': 10., 'pressure': 1.}  # Tolerances for cache search procedure

        # Opening cache as read-only file to look-up stored values
        with open('cache/entropy_table.dat') as cache:
            entries = cache.readlines()[1:]
            valid_entries = []
            for entry in entries:
                try:
                    cached_temp, cached_pres, cached_s0 = entry.split('\t')
                    cached_temp, cached_pres, cached_s0 = float(cached_temp), float(cached_pres), float(cached_s0)
                    temp_error, pres_error = temp - cached_temp, pres - cached_pres
                    if temp_error < tol['temperature'] or pres_error < tol['pressure']:
                        # [0] Temperature [1] Pressure [2] Entropy [3] Squared Error
                        valid_entries += [(cached_temp, cached_pres, cached_s0, (temp_error + pres_error)**2)]
                except Exception as e:
                    raise e

        if len(valid_entries) == 0:  # No valid entries found online database must be accessed
            with requests.Session() as session:
                prog.update(25, 'Loading Session')
                calculator_url = 'http://www.irc.wisc.edu/properties/'
                data = {'units': 'International',
                        'fluid': 'Dry Air',
                        'parameter1': 'T',  # State 1 = Temperature
                        'parameter2': 'P',  # State 2 = Pressure
                        'state1': '{}'.format(temp),  # Degrees Celcius
                        'state2': '{}'.format(pres),  # Absolute Pressure in kPa
                        'calculate': 'Calculate Properties'}
                prog.update(35, 'Posting Request to Database')
                response = session.post(calculator_url, data=data)
                prog.update(90, 'Parsing Response')
                result_hdr = ('<!-- Calculation Results -->', '</table')  # Tuple of start [0] end [1] strings

                raw = response.text.split(result_hdr[0])[-1].split(result_hdr[1])[0]
                filtered = raw.replace('\t', '').replace('\n', '').split('Entropy: ')[-1].split(' J')[0]
                s0 = float(filtered)  # Entropy in J/kg K

                # Writing value to cache and returning
                with open('cache/entropy_table.dat', 'a') as cache:
                    cache.write('\n{:.10f}\t{:.10f}\t{:.10f}'.format(temp, pres, s0))
                prog.update(100, 'Complete')
                return s0
        else:
            closest_match = sorted(valid_entries, key=lambda x: x[-1])[0]  # Returns entry with minimum sq. Error
            prog.update(100, 'Complete')
            return closest_match[2]

    def isobaric_lines(self, plot_limits=(6000, 8000, 0, 800), n_lines=10):
        """ Plots isobaric lines utilizing the specific heat of the fuel/air mixture (gas) to better match the
        combustion and heat rejection process

        :param tuple plot_limits:
        :param int n_lines: Specifies maximum number of isobaric process lines to draw
        :return:
        """
        s_lower, s_upper, t_lower, t_upper = plot_limits

        s_range = np.arange(s_lower, s_upper, (s_upper - s_lower) / 1000.)
        for t_initial in np.linspace(t_lower, t_upper, n_lines):
            t_values = t_initial * np.exp((s_range - s_lower) / self.engine_in.ambient.specific_heat_gas)
            plt.plot(s_range, t_values, alpha=1.0, label='{}'.format(t_initial))

    def plot_stage(self, component_in, s_start):

        if isinstance(component_in, Inlet):
            t_start, t_end = component_in.inflow.t_static, component_in.outflow.t_total
            p_start, p_end = component_in.inflow.p_static, component_in.inflow.p_total
        else:
            t_start, t_end = component_in.inflow.t_total, component_in.outflow.t_total
            p_start, p_end = component_in.inflow.p_total, component_in.inflow.p_total

        delta_s = (component_in.inflow.specific_heat * log(t_end / t_start)) - (component_in.gas_constant
                                                                                * log(p_start / p_end))
        plt.plot(s_start, t_start, marker='o', markerfacecolor='white')
        plt.plot(s_start + abs(delta_s), t_end, marker='o', markerfacecolor='white')
        plt.text(s_start + abs(delta_s), t_end, component_in.outflow.station_number)
        return s_start + abs(delta_s)

    def plot(self):
        """ Generates a plot of the T-s diagram (Temperature vs. Specific entropy) """
        fig = plt.figure('{}Cycle'.format('Ideal' if self.engine_in.ideal_cycle else ''))
        plt.style.use('tudelft')
        s_0 = self.specific_entropy

        # Values used for the Exact Solution
        station_1 = plt.plot(s_0, self.engine_in.ambient.t_static, marker='o')
        print(station_1[0].get_color())
        s_inlet = self.plot_stage(self.engine_in.inlet, s_0)
        s_fan = self.plot_stage(self.engine_in.fan, s_inlet)
        s_lpc = self.plot_stage(self.engine_in.lpc, s_fan)
        s_hpc = self.plot_stage(self.engine_in.hpc, s_lpc)
        s_cc = self.plot_stage(self.engine_in.combustor, s_hpc)
        s_hpt = self.plot_stage(self.engine_in.hpt, s_cc)
        s_lpt = self.plot_stage(self.engine_in.lpt, s_hpt)
        # s_hot_nozzle = self.plot_stage(self.engine_in.nozzle_core, s_lpt)
        # s_cold_nozzle = self.plot_stage(self.engine_in.nozzle_bypass, s_fan)
        # self.isobaric_lines()

        plt.xlabel(r'Specific Entropy $\left[\frac{\mathrm{J}}{\mathrm{kg} \cdot \mathrm{K}}\right]$')
        plt.ylabel(r'Temperature $\left[\mathrm{K}\right]$')
        plt.title(r'Test')
        # plt.axis((2000., 15000, 0., 1000.))
        plt.legend()
        plt.show()


if __name__ == '__main__':
    obj = BraytonCycle(engine_in=Engine(ideal_cycle=False))
    resp = obj.specific_entropy
    obj.plot()

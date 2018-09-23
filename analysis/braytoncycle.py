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
        prog = ProgressBar('Fetching Entropy Value')
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

    # def isobaric_lines(self, plot_limits=(6000, 8000, 0, 800), n_lines=30):
    #     """ Plots isobaric lines utilizing the specific heat of the fuel/air mixture (gas) to better match the
    #     combustion and heat rejection process
    #
    #     :param tuple plot_limits:
    #     :param int n_lines: Specifies maximum number of isobaric process lines to draw
    #     :return:
    #     """
    #     s_lower, s_upper, t_lower, t_upper = plot_limits
    #
    #     s_range = np.arange(s_lower, s_upper, (s_upper - s_lower) / 100.)
    #     for t_initial in np.linspace(t_lower, t_upper, n_lines):
    #         t_values = t_initial * np.exp((s_range - s_lower) / self.engine_in.ambient.specific_heat_air)
    #         plt.plot(s_range, t_values, alpha=1.0, color='black', linewidth=0.5, linestyle='--')

    def isobaric_lines(self, plot_bounds, lower_intercept, upper_intercept, n_lines=5):
        """ Plots isobaric lines utilizing the specific heat of the fuel/air mixture (gas) to better match the
        combustion and heat rejection process

        :param float reference_entropy: Reference Specific Entropy of the system in SI Joule per kilogram Kelvin
        :param tuple intercept_point:
        :param int n_lines: Specifies maximum number of isobaric process lines to draw
        :return:
        """
        s_min, s_max, t_min, t_max = plot_bounds
        delta_s = np.array([lower_intercept[0] - s_min, upper_intercept[0] - s_min])

        # Adding padding to the maximum entropy value
        s_max = s_max * 2.

        t_int = np.array([lower_intercept[1], upper_intercept[1]])
        t_initial = t_int / np.exp(delta_s / self.engine_in.inlet.inflow.specific_heat)
        t_range = np.linspace(t_initial[0], t_initial[1], n_lines)

        s_range = np.arange(s_min, s_max, s_min/100.)
        for t in t_range:
            t_values = t * np.exp((s_range - s_min) / self.engine_in.ambient.specific_heat_air)
            plt.plot(s_range, t_values, alpha=1.0, color='black', linewidth=0.5, linestyle='--')

    def plot_stage(self, stage_in, s_inflow, offset=(10, 10)):

        stg = stage_in

        def entropy_func(t1, t2, p1, p2):
            """ Describes the change in Specific Entropy across the stage in SI Joule per kilogram Kelvin [J/kg K]

            :param float t1: Temperature at the start of the stage in SI Kelvin [K]
            :param float t2: Temperature at the end of the stage in SI Kelvin [K]
            :param float p1: Pressure at the start of the stage in SI Pascal [Pa]
            :param float p2: Pressure at the start of the stage in SI Pascal [Pa]

            :rtype: float
            """
            return stg.inflow.specific_heat * np.log(t2 / t1) - (stg.gas_constant * np.log(p2 / p1))

        def psuedo_t(t1, t2, s_array):
            """ Performs a simple exponential fit for visualization of the interstage values

            :param t1: Temperature at the start of the stage in SI Kelvin [K]
            :param t2: Temperature at the end of the stage in SI Kelvin [K]
            :param np.array s_array: A 1D array of Specific Entropy values in SI Joule per kilogram kelvin [J/kg K]

            :rtype: np.array
            """
            s_start, s_end = s_array[0], s_array[-1]

            return t1 * np.exp(np.log(t2 / t1) * ((s_array - s_start) / (s_end - s_start)))

        if isinstance(stg, Inlet):
            t_inflow, t_outflow = stg.inflow.t_static, stg.outflow.t_total
            p_inflow, p_outflow = stg.inflow.p_static, stg.outflow.p_total
        else:
            t_inflow, t_outflow = stg.inflow.t_total, stg.outflow.t_total
            p_inflow, p_outflow = stg.inflow.p_total, stg.outflow.p_total

        delta_s = entropy_func(t_inflow, t_outflow, p_inflow, p_outflow)
        print(delta_s)

        s_range = np.linspace(s_inflow, s_inflow + delta_s, 100)
        t_range = psuedo_t(t_inflow, t_outflow, s_range)

        bbox = dict(boxstyle="round", fc="0.8")
        arrowprops = dict(
            arrowstyle="->",
            connectionstyle="angle,angleA=0,angleB=90,rad=10",
            color='black')

        # offset = 10
        h_offset, v_offset = offset[0], offset[1]
        plt.annotate(stg.outflow.station_number, (s_inflow + delta_s, t_outflow),
                     xytext=(-2 * h_offset, v_offset), textcoords='offset points',
                     bbox=bbox, arrowprops=arrowprops, fontsize=7)

        plt.plot(s_range, t_range, color='#00A6D6')
        start_marker = plt.plot(s_inflow, t_inflow, marker='o', markerfacecolor='white', markeredgecolor='#00A6D6')
        plt.plot(s_inflow + delta_s, t_outflow, marker='o', markerfacecolor='white', markeredgecolor='#00A6D6')
        return s_inflow + delta_s

    def plot(self):
        """ Generates a plot of the T-s diagram (Temperature vs. Specific entropy) """
        fig = plt.figure('{}Cycle'.format('Ideal' if self.engine_in.ideal_cycle else ''))
        plt.style.use('tudelft')
        s_0 = self.specific_entropy

        # Values used for the Exact Solution
        # print(station_1[0].get_color()) # How to get station color
        s_inlet = self.plot_stage(self.engine_in.inlet, s_0)
        s_fan = self.plot_stage(self.engine_in.fan, s_inlet, offset=(-10, 10))
        s_lpc = self.plot_stage(self.engine_in.lpc, s_fan, offset=(-10, 10))
        s_hpc = self.plot_stage(self.engine_in.hpc, s_lpc)
        s_cc = self.plot_stage(self.engine_in.combustor, s_hpc)
        s_hpt = self.plot_stage(self.engine_in.hpt, s_cc, offset=(-10, 10))
        s_lpt = self.plot_stage(self.engine_in.lpt, s_hpt)
        s_hot_nozzle = self.plot_stage(self.engine_in.nozzle_core, s_lpt)
        s_cold_nozzle = self.plot_stage(self.engine_in.nozzle_bypass, s_fan)

        s_min, s_max = plt.gca().get_xbound()
        t_min, t_max = plt.gca().get_ybound()
        self.isobaric_lines(plot_bounds=(s_min, s_max, t_min, t_max),
                            lower_intercept=(s_inlet, self.engine_in.inlet.inflow.t_static),
                            upper_intercept=(s_hpc, self.engine_in.hpc.outflow.t_total), n_lines=5)

        plt.xlabel(r'Specific Entropy $\left[\frac{\mathrm{J}}{\mathrm{kg} \cdot \mathrm{K}}\right]$')
        plt.ylabel(r'Temperature $\left[\mathrm{K}\right]$')
        plt.title(r'Test')
        plt.axis((s_min, s_max, t_min, t_max))
        plt.legend()
        plt.show()


if __name__ == '__main__':
    obj = BraytonCycle(engine_in=Engine(ideal_cycle=True))
    resp = obj.specific_entropy
    obj.plot()

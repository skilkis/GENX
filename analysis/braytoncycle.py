#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Contains all abstract class definitions  """

from engine import Engine
import numpy as np
import matplotlib.pyplot as plt
import requests
from utils import ProgressBar, Attribute

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
                        'parameter1': 'T',  # Degrees celcius
                        'parameter2': 'P',
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

        #
        #
        # if fetch:
        #     with requests.Session() as session:
        #         prog.update(25, 'Loading Session')
        #         calculator_url = 'http://www.irc.wisc.edu/properties/'
        #         data = {'units': 'International',
        #                 'fluid': 'Dry Air',
        #                 'parameter1': 'T',  # Degrees celcius
        #                 'parameter2': 'P',
        #                 'state1': '{}'.format(temp),  # Degrees Celcius
        #                 'state2': '{}'.format(pres),  # Absolute Pressure in kPa
        #                 'calculate': 'Calculate Properties'}
        #         prog.update(35, 'Posting Request to Database')
        #         response = session.post(calculator_url, data=data)
        #         prog.update(90, 'Parsing Response')
        #         result_hdr = ('<!-- Calculation Results -->', '</table')  # Tuple of start [0] end [1] strings
        #
        #         raw = response.text.split(result_hdr[0])[-1].split(result_hdr[1])[0]
        #         filtered = raw.replace('\t', '').replace('\n', '').split('Entropy: ')[-1].split(' J')[0]
        #         s0 = float(filtered) / 1000  # Entropy in kJ/kg K
        #         prog.update(100, 'Complete')
        # else:
        #
        #
        # return s0

    def isobaric_lines(self, plot_limits=(6000, 8000, 0, 800), n_lines=30):
        """

        :param tuple plot_limits:
        :param int n_lines: Specifies maximum number of isobaric process lines to draw
        :return:
        """
        s_lower, s_upper, t_lower, t_upper = plot_limits

        s_range = np.arange(s_lower, s_upper, (s_upper - s_lower) / 1000.)
        for t_initial in np.linspace(t_lower, t_upper, n_lines):
            t_values = t_initial * np.exp((s_range - s_lower) / self.engine_in.ambient.specific_heat)
            print(s_range - s_lower)
            plt.plot(s_range, t_values, color='black', alpha=0.5, linestyle='-.')





    def plot(self):
        """ Generates a plot of the T-s diagram (Temperature vs. Specific entropy) """
        fig = plt.figure('{}Cycle'.format('Ideal' if self.engine_in.ideal_cycle else ''))
        plt.style.use('ggplot')
        s_0 = self.specific_entropy

        # Values used for the Exact Solution
        station_1 = plt.plot(s_0, self.engine_in.ambient.t_static, marker='o')
        self.isobaric_lines()

        plt.xlabel(r'Specific Entropy $\left[\frac{\mathrm{J}}{\mathrm{kg} \cdot \mathrm{K}}\right]$')
        plt.ylabel(r'Temperature $\left[\mathrm{K}\right]$')
        plt.axis((6000, 8000, 0, 1000))
        plt.show()
        # fig.savefig(fname=os.path.join(working_dir, 'Figures', '%s.pdf' % fig.get_label()), format='pdf')


if __name__ == '__main__':
    obj = BraytonCycle()
    resp = obj.specific_entropy
    obj.plot()
    obj.isobaric_lines()

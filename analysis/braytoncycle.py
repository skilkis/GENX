#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Contains all abstract class definitions  """

from components import AmbientInterface, Nozzle
from directories import DIRS
import numpy as np
import matplotlib.pyplot as plt
import requests
from utils import ProgressBar, Attribute

__author__ = 'San Kilkis'

# TODO Add ideal cycle image
# TODO Add figure save capability
# TODO Make sure static isobar connects point 8 to 0


class LabelConfig(object):

    __slots__ = ['location', 'offset', 'iterable', 'station_number']

    def __init__(self, location='outflow', offset=(-10, 10), station_number=None):
        """

        :param str or collections.Sequence[str] or None location: Defines label location, can be iterable
        :param collections.Sequence[tuple] or tuple offset:
        """

        self.location = location
        self.station_number = station_number

        if isinstance(location, tuple):
            self.iterable = True
            if isinstance(offset[0], tuple):
                self.offset = offset
            else:
                self.offset = (offset, offset)
        else:
            self.iterable = False
            self.offset = offset


class BraytonCycle(object):

    def __init__(self, engine_in=None):
        """

        :param Engine engine_in:
        """

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
        with open(DIRS['ENTROPY_TABLE']) as cache:
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
                with open(DIRS['ENTROPY_TABLE'], 'a') as cache:
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
            plt.plot(s_range, t_values, alpha=1.0, color='black', linewidth=0.5, linestyle='--', zorder=0)

    @staticmethod
    def entropy_func(t1, t2, p1, p2, specific_heat, gas_constant):
        """ Describes the change in Specific Entropy across the stage in SI Joule per kilogram Kelvin [J/kg K]

        :param float t1: Temperature at the start of the stage in SI Kelvin [K]
        :param float t2: Temperature at the end of the stage in SI Kelvin [K]
        :param float p1: Pressure at the start of the stage in SI Pascal [Pa]
        :param float p2: Pressure at the start of the stage in SI Pascal [Pa]
        :param float specific_heat: Specific Heat and Constant Pressure of the current medium
        :param float gas_constant: Universal Gas Constant

        :rtype: float
        """
        return specific_heat * np.log(t2 / t1) - (gas_constant * np.log(p2 / p1))

    @staticmethod
    def create_label(station_number, s, t, offset):
        h_offset, v_offset = offset[0], offset[1]
        bbox = dict(boxstyle='circle', fc="0.8", ec='0.7')
        arrowprops = dict(arrowstyle="->",
                          connectionstyle='angle,angleA={},angleB=180,rad=2'.format(-90 if v_offset > 0 else 90),
                          color='black')
        plt.annotate(station_number, (s, t),
                     xytext=(2. * h_offset, v_offset if v_offset > 0 else v_offset * 1.65),
                     textcoords='offset points',
                     bbox=bbox, arrowprops=arrowprops, fontsize=7,
                     horizontalalignment='center',
                     verticalalignment='left')

    @staticmethod
    def psuedo_t(t1, t2, s_array):
        """ Performs a simple exponential fit for visualization of the interstage values

        :param t1: Temperature at the start of the stage in SI Kelvin [K]
        :param t2: Temperature at the end of the stage in SI Kelvin [K]
        :param np.array s_array: A 1D array of Specific Entropy values in SI Joule per kilogram kelvin [J/kg K]

        :rtype: np.array
        """
        s_start, s_end = s_array[0], s_array[-1]

        return t1 * np.exp(np.log(t2 / t1) * ((s_array - s_start) / (s_end - s_start)))

    def plot_heat_rejection(self, s_lower, s_upper, t_lower, t_upper):

        delta_s = s_upper - s_lower

        s_range = np.linspace(s_lower, s_lower + delta_s, 100)
        t_range = self.psuedo_t(t_lower, t_upper, s_range)

        plt.plot(s_range, t_range, color='#00A6D6', linewidth=1.0, linestyle='--', zorder=0)

    def plot_stage(self, stage_in, s_inflow, label=LabelConfig()):
        """

        :param stage_in:
        :param s_inflow:
        :param LabelConfig label:
        :return:
        """

        stg = stage_in

        # Selecting start/end temperature and pressure depending on stage type
        if isinstance(stg, AmbientInterface):
            t_inflow, t_outflow = stg.inflow.t_static, stg.outflow.t_total
            p_inflow, p_outflow = stg.inflow.p_static, stg.outflow.p_total
        elif isinstance(stg, Nozzle):
            t_inflow, t_outflow = stg.inflow.t_total, stg.outflow.t_static
            p_inflow, p_outflow = stg.inflow.p_total, stg.outflow.p_static
        else:
            t_inflow, t_outflow = stg.inflow.t_total, stg.outflow.t_total
            p_inflow, p_outflow = stg.inflow.p_total, stg.outflow.p_total

        delta_s = self.entropy_func(t_inflow,
                                    t_outflow,
                                    p_inflow,
                                    p_outflow,
                                    stg.inflow.specific_heat,
                                    stg.inflow.gas_constant)

        if self.engine_in.ideal_cycle and abs(delta_s) < 10e-6:  # Extra check to avoid div/0 due to machine precision
            s_range = np.linspace(s_inflow, s_inflow + delta_s, 100)
            t_range = np.linspace(t_inflow, t_outflow, 100)
        else:
            s_range = np.linspace(s_inflow, s_inflow + delta_s, 100)
            t_range = self.psuedo_t(t_inflow, t_outflow, s_range)

        # Creating Station Label
        if label.iterable:
            for i, loc in enumerate(label.location):
                self.create_label(getattr(stg, loc).station_number if label.station_number is None else
                                  label.station_number[i],
                                  s_inflow if loc == 'inflow' else s_inflow + delta_s,
                                  t_inflow if loc == 'inflow' else t_outflow, label.offset[i])
        else:
            loc = label.location
            if loc is not None:
                self.create_label(getattr(stg, loc).station_number if label.station_number is None else
                                  label.station_number,
                                  s_inflow if loc == 'inflow' else s_inflow + delta_s,
                                  t_inflow if loc == 'inflow' else t_outflow, label.offset)

        plt.plot(s_range, t_range, color='#00A6D6')
        plt.plot(s_inflow, t_inflow,
                 marker='o',
                 markerfacecolor='white',
                 markeredgecolor='#00A6D6',
                 markersize=2.0)  # Start Mrk.
        plt.plot(s_inflow + delta_s, t_outflow,
                 marker='o',
                 markerfacecolor='white',
                 markeredgecolor='#00A6D6',
                 markersize=2.0)  # End
        return s_inflow + delta_s, t_outflow

    def plot(self):
        """ Generates a plot of the T-s diagram (Temperature vs. Specific entropy) """
        fig = plt.figure('{}Cycle'.format('Ideal' if self.engine_in.ideal_cycle else ''))
        plt.style.use('tudelft')
        s_0, t_0 = self.specific_entropy, self.engine_in.interface.inflow.t_static

        # LabelConfigs
        station_25 = LabelConfig(offset=(-4.5, 30) if self.engine_in.ideal_cycle else (-6.5, 25))

        # Values used for the Exact Solution
        # print(station_1[0].get_color()) # How to get station color
        s_interface, t_interface = self.plot_stage(self.engine_in.interface,
                                                   s_0, LabelConfig(('inflow', 'outflow'), ((-20, 10), (-12.5, 12.5)),
                                                                    station_number=('0', '1,2')))
        s_inlet, t_inlet = self.plot_stage(self.engine_in.inlet, s_interface, LabelConfig(None))
        s_fan, t_fan = self.plot_stage(self.engine_in.fan, s_inlet, LabelConfig(offset=(-8.5, 17.5)))
        s_lpc, t_lpc = self.plot_stage(self.engine_in.lpc, s_fan, station_25)
        s_hpc, t_hpc = self.plot_stage(self.engine_in.hpc, s_lpc)
        s_cc, t_cc = self.plot_stage(self.engine_in.combustor, s_hpc, LabelConfig(offset=(10, -10)))
        s_hpt, t_hpt = self.plot_stage(self.engine_in.hpt, s_cc)
        s_lpt, t_lpt = self.plot_stage(self.engine_in.lpt, s_hpt, LabelConfig(offset=(10, 10), station_number='5,7'))

        s_core, t_core = self.plot_stage(self.engine_in.nozzle_core, s_lpt)
        s_bypass, t_bypass = self.plot_stage(self.engine_in.nozzle_bypass, s_fan,
                                             LabelConfig(('inflow', 'outflow'), ((10, 10), (15, 30))))

        # Getting Plot Limits
        s_min, s_max = plt.gca().get_xbound()
        t_min, t_max = plt.gca().get_ybound()

        # Percentage Pad
        pad_factor = 0.025
        s_min, s_max = s_min * (1. - pad_factor), s_max * (1. + pad_factor)
        t_min, t_max = t_min * (1. - pad_factor), t_max * (1. + pad_factor)

        # Plotting Heat Rejection (Ambient Process)
        self.plot_heat_rejection(s_0, s_core, t_0, t_core)

        # Plotting Isobaric Lines
        self.isobaric_lines(plot_bounds=(s_min, s_max, t_min, t_max),
                            lower_intercept=(s_inlet, self.engine_in.inlet.inflow.t_static),
                            upper_intercept=(s_hpc, self.engine_in.hpc.outflow.t_total), n_lines=5)

        plt.xlabel(r'Specific Entropy $\left[\frac{\mathrm{J}}{\mathrm{kg} \cdot \mathrm{K}}\right]$')
        plt.ylabel(r'Temperature $\left[\mathrm{K}\right]$')
        plt.title(r'{} {} Cycle Diagram'.format(self.engine_in.__name__,
                                                'Ideal' if self.engine_in.ideal_cycle else 'Real'))
        plt.axis((s_min, s_max, t_min, t_max))
        plt.show()


if __name__ == '__main__':
    from engine import Engine
    obj = BraytonCycle(engine_in=Engine(filename='GENX.cfg', ideal_cycle=True))
    resp = obj.specific_entropy
    obj.plot()

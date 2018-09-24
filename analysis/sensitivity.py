#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Contains all abstract class definitions  """

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from utils import Attribute
from directories import *
import os

__author__ = 'San Kilkis'

# TODO Add ideal cycle image
# TODO Add figure save capability
# TODO Make sure static isobar connects point 8 to 0


class Sensitivity(object):

    def __init__(self, engine_in=None):
        """

        :param Engine engine_in:
        """
        self.engine_in = engine_in
        self.design_variable, self.design_range = None, None  # TODO Remove when functionality to plot 1 var is required
        self.filename, self.ideal_cycle, _, _, self.ambient = self.engine_in.args
        self.slope_cache = {'thrust': {}, 'sfc': {}}

        if self.design_variable is None:
            self.design_variable = ['eta_fan', 'eta_lpc', 'eta_hpc', 'eta_lpt', 'eta_hpt', 'eta_mech',
                                    'eta_cc', 'eta_nozzle', 'eta_inlet']
            self.design_range = None
        else:
            self.design_variable = (self.design_variable, )  # Prevents looping through the string below

    @staticmethod
    def func(x, a):
        """ Defines a linear regression function without intercept y(x) = a*x

        :param x: Value(s) on the x-axis which correspond to the disk_loading
        :type x: int, float, list
        :param a: slope
        """
        return a * x

    @Attribute
    def param_sim(self):

        param_list = ['combustion_temperature', 'bypass_ratio', 'pr_cc', 'pr_fan', 'pr_lpc', 'pr_hpc']
        output = []

        for i, var in enumerate(param_list):
            engine_sim = Engine(self.filename, self.ideal_cycle, var, self.design_range, self.ambient)

            percentage = ((engine_sim.design_range / engine_sim.design_range[engine_sim.original_index]) - 1.) * 100
            thrust_response = engine_sim.thrust
            sfc_response = engine_sim.sfc

            # Appending to the output_list
            output += [(percentage, thrust_response, sfc_response)]

            # Calculating Slopes and adding to the :py:attr`slope_cache`
            self.slope_cache['thrust'][var] = curve_fit(self.func, percentage, thrust_response)[0][0]
            self.slope_cache['sfc'][var] = curve_fit(self.func, percentage, sfc_response)[0][0]

        return output

    def plot_param(self):
        plt.style.use('tudelft')
        fig, (thrust, sfc) = plt.subplots(2, 1, num='{} Efficiency Sensitivity'.format(self.engine_in.__name__),
                                          sharex='all')

        # Initializing Labels
        thrust.set_ylabel(r'Thrust $\left[\mathrm{N}\right]$')
        sfc.set_ylabel(r'Specific Fuel Consumption $\left[\frac{\mathrm{g}}{\mathrm{kN} \cdot \mathrm{s}}\right]$')
        thrust.set_xlabel('')
        thrust.set_title('{} Parameter Sensitivity'.format(self.engine_in.__name__))

        linestyles = [':', '-.', '-']

        label_list = [r'$T_{4}$',
                      'BPR',
                      r'$\Pi_{\mathrm{cc}}$',
                      r'$\Pi_{\mathrm{fan}}$',
                      r'$\Pi_{\mathrm{lpc}}$',
                      r'$\Pi_{\mathrm{hpc}}$']

        for i, entry in enumerate(self.param_sim):
            cycle_count = i % len(linestyles)
            style = linestyles[cycle_count]

            percent, thrust_response, sfc_response = entry

            thrust.plot(percent, thrust_response, label=label_list[i], linestyle=style, linewidth=1.0)
            sfc.plot(percent, sfc_response, label=label_list[i], linestyle=style, linewidth=1.0)

        thrust.plot(0., self.engine_in.thrust, marker='o',
                    linewidth=0.,
                    markerfacecolor='white',
                    markeredgecolor='black',
                    label='Design Point')

        sfc.plot(0., self.engine_in.sfc, marker='o',
                 linewidth=0.,
                 markerfacecolor='white',
                 markeredgecolor='black',
                 label='Design Point')

        plt.legend(loc='right', fontsize=8)
        sfc.set_xlabel(r'Percentage Change of Design Parameter $\left[\%\right]$')
        plt.show()

    def write_csv(self):
        with open(os.path.join(DIRS['CSV_DIR'], '{}_param_slope.csv'.format(self.engine_in.__name__)), "w") as csv:
            for key, sfc_slope, thrust_slope in zip(obj.slope_cache['sfc'].keys(), obj.slope_cache['sfc'].values(),
                                                    obj.slope_cache['thrust'].values()):
                csv.write('{}, {}, {}\n'.format(key, sfc_slope, thrust_slope))

    def plot_eta(self):
        plt.style.use('tudelft')
        fig = plt.figure('{}_eta_sens'.format(self.engine_in.__name__))
        fig, (thrust, sfc) = plt.subplots(2, 1, num='{} Efficiency Sensitivity'.format(self.engine_in.__name__),
                                          sharex='all')

        # Initializing Labels
        thrust.set_ylabel(r'Thrust $\left[\mathrm{N}\right]$')
        sfc.set_ylabel(r'Specific Fuel Consumption $\left[\frac{\mathrm{g}}{\mathrm{kN} \cdot \mathrm{s}}\right]$')
        thrust.set_xlabel('')
        thrust.set_title('{} Efficiency Sensitivity'.format(self.engine_in.__name__))

        linestyles = [':', '-.', '-']
        for i, var in enumerate(self.design_variable):
            cycle_count = i % len(linestyles)
            style = linestyles[cycle_count]
            engine_sim = Engine(self.filename, self.ideal_cycle, var, self.design_range, self.ambient)
            thrust.plot(engine_sim.design_range, engine_sim.thrust,
                        label=r'$\eta_{\mathrm{%s}}$' % var.split('_')[-1],
                        linestyle=style,
                        linewidth=1.0)
            sfc.plot(engine_sim.design_range, engine_sim.sfc,
                     label=r'$\eta_{\mathrm{%s}}$' % var.split('_')[-1],
                     linestyle=style,
                     linewidth=1.0)

        # plt.xlabel(r'Specific Entropy $\left[\frac{\mathrm{J}}{\mathrm{kg} \cdot \mathrm{K}}\right]$')
        # plt.ylabel(r'Temperature $\left[\mathrm{K}\right]$')
        # plt.title(r'{} Sensitivity Analysis'.format(self.engine_in.__name__))
        plt.legend(loc='right', fontsize=8)
        sfc.set_xlabel(r'Efficiency $\left[-\right]$')
        x_min, x_max = plt.gca().get_xbound()
        y_min, y_max = plt.gca().get_ybound()
        plt.axis([x_min, x_max, y_min, y_max])
        plt.show()


if __name__ == '__main__':
    from engine import Engine
    obj = Sensitivity(engine_in=Engine())
    obj.plot_eta()
    obj.plot_param()
    obj.write_csv()

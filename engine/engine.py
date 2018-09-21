#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Contains all abstract class definitions  """

from engineparser import EngineParser
from definitions import FlowCondition
import numpy as np
try:
    import ConfigParser as config
except ImportError:
    import configparser as config

__author__ = 'San Kilkis'


class Engine(EngineParser):

    def __init__(self, filename='GE90.cfg', isentropic=True, design_variable='eta_cc',
                 ambient_conditions=FlowCondition(mach=0.8, p_static=22632, t_static=216, medium='air')):
        """
        :param str filename: Filename w/ extension of desired engine
        :param bool isentropic: Toggles if the compression and expansion processes are isentropic
        :param str design_variable: Specifies which design variable to investigate
        :param FlowCondition inflow: Specifies the flow the engine is subject to
        """
        super(Engine, self).__init__(filename)
        self.isentropic = isentropic
        self.design_variable = design_variable
        self.ambient_conditions = ambient_conditions

        # Test Range Bounds for the Sensitivity Analysis
        upper, lower = self.get_bounds()
        self.test_range = np.linspace(lower, upper, 50)

    def get_bounds(self):
        """ Automatically obtains sensitivity analysis for a variable """
        current_value = getattr(self, self.design_variable)
        upper, lower = 0.9 * current_value,  1.1 * current_value
        if 'eta' in self.design_variable:
            upper = 1.0
            lower = 0.9
        return upper, lower


if __name__ == '__main__':
    obj = Engine()
    print(obj.eta_nozzle)
    print(obj.test_range)

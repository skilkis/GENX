#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Provides all derived/non-derived inputs of the CH-53D Helicopter to be used later in performance calculations """

from definitions import Stage

__author__ = 'San Kilkis'


class Inlet(Stage):

    def __init__(self, input_flow, eta=None):
        eta = self.engine_data['efficiencies']['eta_inlet'] if eta is None else eta
        super(self.__class__, self).__init__(input_flow, eta)

    def mass_flow(self):
        return


if __name__ == '__main__':
    from definitions import FlowCondition
    ambient_conditions = FlowCondition(mach=0.8, t_static=216, p_static=22632)
    obj = Inlet(input_flow=ambient_conditions)

# working_dir = os.path.dirname(os.path.realpath(__file__))

# TODO Remove the following attributes and put them into OOP for lazy-evaluation

# TODO consider making use of https://docs.python.org/2/library/trace.html for dependency tracking

#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Provides all derived/non-derived inputs of the CH-53D Helicopter to be used later in performance calculations """

from base import Base
from utils import Attribute

__author__ = 'San Kilkis'


class Stage(Base):

    def __init__(self, input_flow, eta):
        self.input_flow = input_flow
        self.eta = eta

    @Attribute
    def mass_in(self):
        """ Mass flow into the stage in SI kilogram per second [kg/s]

        :return:
        """
        return self.input_conditions.mass_in
# working_dir = os.path.dirname(os.path.realpath(__file__))

# TODO Remove the following attributes and put them into OOP for lazy-evaluation

# TODO consider making use of https://docs.python.org/2/library/trace.html for dependency tracking

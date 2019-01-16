#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Performs a simple analysis for the fuel flow required to sustain combustion as well as computing air-fuel ratios """

from definitions import Attribute, Stage, FlowCondition
from directories import DIRS
import os


class OperatingCondition(object):

    __slots__ = ['name', 'net_thrust', 'inflow', 'outflow']

    def __init__(self, data_tuple):
        self.name = None

    def __repr__(self):
        return '<OperatingCondition {}>'.format(self.name)


class CombustionAnalysis(object):

    def __init__(self, engine_name='PW4056'):
        """
        :param str engine_name: Sets the engine name used to access combustion chamber and experimental data files
        """
        self.engine_name = engine_name

    @Attribute
    def operating_conditions(self):
        return None

    def parse_data(self):
        with open(os.path.join(DIRS['DATA_DIR'], '{}_experiment.csv'.format(self.engine_name))) as f:
            try:
                lines = f.readlines()
                keys = [key for key in lines[0].split(',') if key != '\n']
                data = [[float(entry) if entry.replace('.', '').isdigit() else entry for i, entry in
                         enumerate(line.split(',')) if entry != '\n'] for line in lines[1:]]  # transforms .csv to dict
                data_dict = [{keys[i]: entry for i, entry in enumerate(condition)} for condition in data]
                return data_dict
            except Exception as e:
                # TODO add a more comprehensive input file reading/checking mechanism
                raise e

    def read_specs(self):
        return NotImplementedError('This feature has not yet been introduced')


if __name__ == '__main__':
    obj = CombustionAnalysis()
    obj.parse_data()


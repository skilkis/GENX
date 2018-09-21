#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Contains all abstract class definitions  """

__author__ = 'San Kilkis'


class AttrDict(dict):
    """ Nested Attribute Dictionary

    A class to convert a nested Dictionary into an object with key-values
    accessibly using attribute notation (AttrDict.attribute) in addition to
    key notation (Dict["key"]). This class recursively sets Dicts to objects,
    allowing you to recurse down nested dicts (like: AttrDict.attr.attr)
    """

    def __init__(self, mapping):
        super(AttrDict, self).__init__()  # Initializes the dictionary object w/ mapping
        for key, value in mapping.items():
            self.__setitem__(key, value)

    def __setitem__(self, key, value):
        if isinstance(value, dict):  # If passed dictionary mapping is a dictionary instead of key, value recurse
            value = AttrDict(value)
        super(AttrDict, self).__setitem__(key, value)

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError(item)

    __setattr__ = __setitem__


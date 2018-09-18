#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Provides all derived/non-derived inputs of the CH-53D Helicopter to be used later in performance calculations """

from math import pi, sqrt
from functools import update_wrapper
import os

# working_dir = os.path.dirname(os.path.realpath(__file__))

# TODO Remove the following attributes and put them into OOP for lazy-evaluation

# Inputs
g = 9.81  # Gravitational Acceleration [m/s**2]

m = 19051  # mass [kg]
W = m * g  # Weight [N]
D = 21.95  # Rotor Diameter
R = D / 2.0  # Rotor Radius [m]
n = 6  # Number of Rotor Blades
c = 0.76  # Blase chord [m]
l_tr = 13.62  # Tail Rotor Length (WRT main rotor) [m]
D_tr = 4.9  # Tail Rotor Diameter [m]
R_tr = D_tr / 2.0  # Tail Rotor Radius [m]
FM = 0.69  # CH-53 Value of Figure of Merit from Sikorsky Archives
V_cr_kmh = 278.4  # Assumed Cruise speed used for tip mach no calculation [kmh]
V_cr = V_cr_kmh / 3.6  # Cruise speed used for tip mach no calculation [m/s]

k = 1.15  # Assumed k factor for BEM rotor induced power
k_tr = 1.4  # Assumed k_tr for tail rotor BEM Power
c_tr = 0.29  # Tail Rotor Chord Length
n_tr = 4.0  # Number tail rotor Blades
omega_tr_rpm = 699  # Tail Rotor Speed [rpm] from sikorsky archives
omega_tr = (omega_tr_rpm * 2 * pi) / 60.0  # Tail Rotor Rotational Velocity [rad/s]

#  Standard Sea Level Conditions
rho = 1.225  # Density kg/m^3
T_inf = 288.15  # Freestream Temperature

omega = 19.37  # Main rotor Rotation rate [rad/s] from sikorsky archives

# Total Engine Power
P_e = 2926.872 * 2000  # Total Engine Power [W]

#  Calculate Main Rotor Blade Solidity (psi)
psi = (n * c) / (pi * R)

#  Calculate Tail Rotor Blade Solidity
psi_tr = (n_tr * c_tr) / (pi * R_tr)

#  Calc Disk Loading
DL = W / (pi * R ** 2)
# print 'Disk Loading =', DL, '[N/m^2]'

#  Calc Tip Mach Number
a_inf = sqrt(1.4 * 287.1 * T_inf)  # Freestream Speed of Sound
V_t = omega * R
M_t = V_t / a_inf  # Tip Mach number

C_dp = 0.0251  # Blade average drag coefficient

#  Equivalent Flat Plate Area
sum_cds = 4.23  # This is the Equivalent Flat Plate Area estimated from pg 52 of reader

# TODO consider making use of https://docs.python.org/2/library/trace.html for dependency tracking


class Attribute(property):
    """ A decorator that is used for lazy evaluation of an object attribute.
    property should represent immutable data, as it replaces itself.

    .. NOTE: I AM NOT THE ORIGINAL AUTHOR, THIS IS FROM JACK MANEY'S REPO

    https://github.com/jackmaney/lazy-property/blob/master/lazy_property/__init__.py
    """

    # __slots__ = ['method', '__name__', 'cache_name', 'fget', 'fset', 'fdel', 'doc']

    def __init__(self, method, fget=None, fset=None, fdel=None, doc=None):
        self.method = method
        self.cache_name = "_{}".format(self.method.__name__)

        doc = doc or method.__doc__
        super(self.__class__, self).__init__(fget=fget, fset=fset, fdel=fdel, doc=doc)

        update_wrapper(self, method)

    # def __get__(self, instance, owner=None):
    #     if instance is None:
    #         return self
    #     value = self.method(instance)
    #     setattr(instance, self.__name__, value)
    #     return value

    def __get__(self, instance, owner=None):

        if instance is None:
            return self

        if hasattr(instance, self.cache_name):
            result = getattr(instance, self.cache_name)
        else:
            if self.fget is not None:
                result = self.fget(instance)
            else:
                result = self.method(instance)

            setattr(instance, self.cache_name, result)

        return result

    def __set__(self, instance, value):

        if instance is None:
            raise AttributeError

        if self.fset is None:
            setattr(instance, self.cache_name, value)
        else:
            self.fset(instance, value)


class Constants(object):

    """ An OOP Version of the above constants to use for the following part of this assignment, supporting lazy
     evaluation where not every attribute or property will be triggered at run-time, thus increasing performance """

    @Attribute
    def g(self):
        """ Gravitational Acceleration in SI meter per second [m /s]"""
        print('I evaluated I am G0')
        return g

    @Attribute
    def rho(self):
        """ Atmospheric Density in SI kilogram per meter cubed [kg/m^3]"""
        return self.g * rho

    @Attribute
    def temperature(self):
        """ Atmospheric Temperature in SI Kelvin [K] """
        return T_inf
    #
    # @Attribute
    # def mass_mtow(self):
    #     """ Gross mass of the CH-53 in SI kilogram [kg] """
    #     return m
    #
    # @Attribute
    # def weight_mtow(self):
    #     """ Gross weight of the CH-53 in SI Newton [N] """
    #     return self.mass_mtow * self.g
    #
    # @Attribute
    # def main_rotor(self):
    #     """ Contains all main-rotor attributes of the CH-53 in SI units """
    #     main_rotor_tuple = namedtuple('main_rotor', ['diameter',
    #                                                  'radius',
    #                                                  'blade_number',
    #                                                  'chord',
    #                                                  'omega',
    #                                                  'solidity',
    #                                                  'tip_speed',
    #                                                  'tip_mach'])
    #     return main_rotor_tuple(D, R, n, c, omega, psi, omega*R, omega*R/self.speed_of_sound)
    #
    # @Attribute
    # def tail_arm(self):
    #     """ Distance from the main-rotor hub to the tail-rotor hub of the CH-53 in SI meter [m] """
    #     return l_tr
    #
    # @Attribute
    # def tail_rotor(self):
    #     """ Contains all tail-rotor attributes of the CH-53 in SI units """
    #     tail_rotor_tuple = namedtuple('tail_rotor', ['diameter',
    #                                                  'radius',
    #                                                  'blade_number',
    #                                                  'chord',
    #                                                  'omega',
    #                                                  'solidity',
    #                                                  'tip_speed',
    #                                                  'tip_mach'])
    #     return tail_rotor_tuple(D_tr,
    #                             R_tr,
    #                             n_tr,
    #                             c_tr,
    #                             omega_tr,
    #                             psi_tr,
    #                             omega_tr*R_tr,
    #                             omega_tr*R_tr/self.speed_of_sound)
    #
    # @Attribute
    # def figure_of_merit(self):
    #     """ CH-53 Value of Figure of Merit from Sikorsky Archives """
    #     return FM
    #
    # @Attribute
    # def cruise_velocity(self):
    #     return V_cr
    #
    # @Attribute
    # def k_factor(self):
    #     return k
    #
    # @Attribute
    # def k_factor_tail(self):
    #     return k_tr
    #
    # @Attribute
    # def power_avaliable(self):
    #     """ Total Available Engine Power in SI Watt [W] """
    #     return P_e
    #
    # @Attribute
    # def disk_loading(self):
    #     """ Disk Loading of the CH-53 in SI Newton per meter squared [N/m^2] """
    #     return self.weight_mtow / (pi * (self.main_rotor.radius ** 2))
    #
    # @Attribute
    # def speed_of_sound(self):
    #     """ Freestream Speed of Sound in SI meter per second [m/s] """
    #     return sqrt(1.4 * 287.1 * self.temperature)
    #
    # @Attribute
    # def average_drag(self):
    #     """ Blade Average Drag Coefficient """
    #     return C_dp
    #
    # @Attribute
    # def flat_plate_area(self):
    #     """ Equivalent Flat Plate Area of estimated from pg. 52 of the reader """
    #     return sum_cds
    #
    # @Attribute
    # def weights(self):
    #     """ Instantiates the Weight Estimating Relationships class to be accessed by the rest of the class
    #
    #     :return: Class containing all Component Weights
    #     """
    #     return ComponentWeights()
    #
    # @Attribute
    # def inertia_blade(self):
    #     """ Single blade Mass Moment of Inertia about the flapping hinge assuming that the blade length runs from
    #     hub-center to tip.
    #
    #     :return: Mass Moment of Inertia in SI kilogram meter squared [kg m^2]
    #     """
    #     return (1.0/3.0) * \
    #            (self.weights.kg_to_lbs(self.weights.W_2A, power=-1) /
    #             self.main_rotor.blade_number) * self.main_rotor.radius**2
    #
    # @Attribute
    # def lift_gradient(self):
    #     """ Lift coefficient gradient of the CH-53D main rotor (SC1095 Airfoil)
    #
    #     :return: Lift Coefficient Gradient in SI one over radians [1/rad]
    #     """
    #     return LiftGradient().gradient
    #
    # @Attribute
    # def lock_number(self):
    #     """ Represents the ratio of aerodynamic excitation forces to the inertial forces on the blade
    #
    #     :return: Non-Dimensional Lock Number [-]
    #     """
    #     return (self.rho * self.lift_gradient * self.main_rotor.chord * (self.main_rotor.radius ** 4)) \
    #         / self.inertia_blade


if __name__ == '__main__':
    obj = Constants()
    print(obj)
    print(obj.g)
    print(obj.rho)
    obj.g = 20
    print(obj.g)
    print(obj.rho)


from dolfin import *
import numpy as np

"""
Liner retreat.
"""

class LengthInputsLinear(object):

    # Rate of advance or retreat in meters per year
    def __init__(self, k = 0.):
        self.k = k


    # Offset of length from initial position
    def get_L_offset(self, t):
        return self.k * t


    # Time derivative of length of time t
    def get_dLdt(self, t):
        return self.k

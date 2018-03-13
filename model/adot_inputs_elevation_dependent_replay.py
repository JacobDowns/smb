from dolfin import *
import numpy as np

"""
An elevation dependent smb function.
"""

class AdotInputsElevationDependentReplay(object):

    # Rate of advance or retreat in meters per year
    def __init__(self, k = 0.):
        self.k = k


    # Return the smb expression, just ignore the surface
    def get_adot_exp(self, S, adot_param):
        return Constant(-4.) * ((S / Constant(4000.0)) - Constant(1.))**2 + adot_param

    # Update the smb expression
    def update(self, i, t, L):
        pass

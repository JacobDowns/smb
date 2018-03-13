from dolfin import *
import numpy as np

"""
An elevation dependent smb function.
"""

class AdotInputsElevationDependent(object):

    # Return the smb expression, just ignore the surface
    def get_adot_exp(self, S, adot_param):
        return Constant(-3.) * ((S / Constant(3500.0)) - Constant(1.))**2 + adot_param

    # Update the smb expression
    def update(self, i, t, L):
        pass

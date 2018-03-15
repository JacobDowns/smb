from dolfin import *
import numpy as np

"""
A linear smb function.
"""

class AdotInputsLinear(object):

    def __init__(self, adot_max = 0.5, L_steady = 425e3):

        # Surface mass balance expression
        class Adot(Expression):
            def __init__(self, L_initial, degree=1):
                self.L = L_initial
                self.degree = degree

            def eval(self, values, x):
                x = x[0]*self.L
                values[0] = adot_max*(1.0 - 2.0*(x / L_steady))

        self.adot_exp = Adot(L_steady, degree = 1)


    # Return the smb expression, just ignore the surface
    def get_adot_exp(self, S, adot_param = None):
        return self.adot_exp


    # Update the smb expression
    def update(self, t, L):
        self.adot_exp.L = L

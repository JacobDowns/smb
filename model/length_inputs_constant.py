from dolfin import *
import numpy as np

"""
A linear smb function.
"""

class LengthInputsConstant(object):

    # Offset of length from initial position
    def get_L_offset(self, t):
        return 0.0


    # Time derivative of length of time t
    def get_dLdt(self, t):
        return 0.0

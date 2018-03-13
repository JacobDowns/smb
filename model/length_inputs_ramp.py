from dolfin import *
import numpy as np

"""
Retreat at a roughly linear rate, but accelerate slowly at first. 
"""

class LengthInputRamp(object):


    # Offset of length from initial position
    def get_L_offset(self, t):
        return - 25.*(t + 100.*np.log(100.) - 100.*np.log(100. + t))


    # Time derivative of length of time t
    def get_dLdt(self, t):
        return  -25*(t / (100. + t))

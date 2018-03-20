from dolfin import *
import numpy as np
from scipy.interpolate import UnivariateSpline

"""
Determine a length function by adding noise between observation points and
interpolating.
"""

class LengthInputsInterp(object):

    # Rate of advance or retreat in meters per year
    def __init__(self, ts, offsets, intermediate_points):

        # The number of intermediate points between every two observations

        self.ts = ts
        self.offsets = offsets

        self.ts_full = np.zeros( len(ts) + (len(ts) - 1)*intermediate_points)


        #self.set(ts, offsets)



    # Offset of length from initial position
    def get_L_offset(self, t):
        return float(self.L_interp(t))


    # Time derivative of length of time t
    def get_dLdt(self, t):
        return float(self.dLdt_interp(t))


    """
    # This is for convenince when doing enembles of runs
    def set(self, ts, offsets):
        self.ts = ts
        self.offsets = offsets
        self.L_interp = UnivariateSpline(self.ts, self.offsets, k = 2, s =  0.01)
        self.dLdt_interp = self.L_interp.derivative()"""

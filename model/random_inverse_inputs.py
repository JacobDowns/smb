from common_inputs1 import *
import numpy as np
from scipy.interpolate import UnivariateSpline

"""
Model inputs for the reverse model. This includes common inputs as well as glacier
length L.
"""

class RandomInverseInputs(CommonInputs1):

    def __init__(self, input_file_name):
        super(RandomInverseInputs, self).__init__(input_file_name)

        ### Terminus position "observations"
        ########################################################################

        # Times
        self.ts = np.array([0.0, 1200.0, 2000.0, 3000.0, 4000.0, 5000.0, 6000.0])
        # Lengths
        self.Ls = np.array([500e3, 480e3, 455e3, 425e3, 390e3, 360e3, 340e3])

        # Add random noise to the obervations
        self.randomize()

        # Initialize L and dLdt
        self.L = self.get_L(0.)
        self.dLdt = self.get_dLdt(0.)


    ### Randomize the times and lenghts by adding some Gaussian noise
    def randomize(self):
        t_noise = np.sqrt(100.) * np.random.randn(len(self.ts))
        L_noise = np.sqrt(1000.0) * np.random.randn(len(self.Ls))
        t_noise[0] = 0.
        L_noise[0] = 0.
        self.ts_rand = self.ts + t_noise
        self.Ls_rand = self.Ls + L_noise
        self.L_interp = UnivariateSpline(self.ts_rand, self.Ls_rand, k = 3, s =  0.01)
        self.dLdt_interp = self.L_interp.derivative()


    ### Return L
    def get_L(self, t):
        return float(self.L_interp(t))


    ### Return dLdt
    def get_dLdt(self, t):
        return float(self.dLdt_interp(t))


    ### Get inputs for the inverse model
    def assign_inputs(self, t, dt):
        # Model inputs are assigned based on current time
        self.B_exp.L = self.get_L(t)
        self.beta2_exp.L = self.get_L(t)
        self.B.interpolate(self.B_exp)
        self.beta2.interpolate(self.beta2_exp)

        # The value of L to use at this time step is the future L at t + dt
        self.L = self.get_L(t + dt)
        self.dLdt = self.get_dLdt(t + dt)

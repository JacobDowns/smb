from dolfin import *
import numpy as np
from common_inputs import *

"""
Inverse model inputs, which includes the glacier length through time.
"""

class InverseInputs(CommonInputs):

    def __init__(self, input_file_name, L_offset_func, dLdt_func, adot_inputs):
        
        super(InverseInputs, self).__init__(input_file_name)

        # Glacer length
        self.L_offset_func = L_offset_func
        # Time derivative of L
        self.dLdt_func = dLdt_func
        # Initial glacier length
        self.L_init = float(self.input_functions['L0'])
        # Initialize glacier length 
        self.L = self.get_L(0.0)
        # Initialize dLdt
        self.dLdt = self.get_dLdt(0.0)
        # Adot inputs defines the form of the SMB
        self.adot_inputs = adot_inputs


    # Get glacier length at time t
    def get_L(self, t):
        return self.L_init + self.L_offset_func(t)


    # Get rate of change of glacier length
    def get_dLdt(self, t):
        return self.dLdt_func(t)


    # Return the smb expression
    def get_adot_exp(self, S, adot_param):
        return self.adot_inputs.get_adot_exp(S, adot_param)        


    # Update inputs that change with length, iteration, time, and time step
    def update_inputs(self, L, t, dt):
        # Interpolate Length dependent inputs
        self.update_interp_all(L)
        # Update adot expression
        self.adot_inputs.update(t, L)
        # The value of L to use at this time step is the future L at t + dt
        self.L = self.get_L(t + dt)
        self.dLdt = self.get_dLdt(t + dt)

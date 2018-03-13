from dolfin import *
import numpy as np
from common_inputs import *

"""
Standard forward model inputs.
"""

class InverseInputs(CommonInputs):

    def __init__(self, input_file_name, adot_inputs, length_inputs, dt, N):

        super(InverseInputs, self).__init__(input_file_name, adot_inputs)

        # Encapsulates glacier lenth inputs (determines L and dLdt through time)
        self.length_inputs = length_inputs
        # Time Step
        self.dt = dt
        # Number of time steps to take
        self.N = N
        # Glacier length
        self.L = self.L_init
        # Rate of change of glacier length
        self.dLdt = self.length_inputs.get_dLdt(0.0)


    # Get glacier length at time t
    def get_L(self, t):
        return self.L_init + self.length_inputs.get_L_offset(t)


    # Get rate of change of glacier length
    def get_dLdt(self, t):
        return self.length_inputs.get_dLdt(t)


    # Update inputs that change with length, iteration, time, and time step
    def update_inputs(self, i, t, dt):
        # Assign bed function
        self.bed_inputs.update(self.get_L(t))
        # Update adto expression
        self.adot_inputs.update(i, t, self.get_L(t))
        # The value of L to use at this time step is the future L at t + dt
        self.L = self.get_L(t + dt)
        self.dLdt = self.get_dLdt(t + dt)

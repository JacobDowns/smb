from dolfin import *
from common_inputs1 import *
import numpy as np

"""
Model inputs for the reverse model. This includes common inputs as well as glacier
length L.
"""

class InverseInputs1(CommonInputs1):

    def __init__(self, input_file_name):
        super(InverseInputs1, self).__init__(input_file_name)
        self.L = self.get_L(0.)
        self.dLdt = self.get_dLdt(0.)


    ### Return L
    def get_L(self, t):
        return self.L_init - 25.*t


    ### Return dLdt
    def get_dLdt(self, t):
        return -25.


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

from dolfin import *
from common_inputs1 import *
import numpy as np

"""
Model inputs for the reverse model. This includes common inputs as well as glacier
length L.
"""

class InverseInputs1(CommonInputs1):

    def __init__(self, input_file_name):
        super(InverseInputs, self).__init__(input_file_name)
        self.update(0.0)

    # Update time
    def update(self, t):
        #self.dLdt = (2.0 / 100.0) * t
        #self.L = self.L_init +  (1. / 100.0) * t**2
        self.dLdt = -25.0
        self.L = self.L_init + self.dLdt * t
        #C = (2.*np.pi) / 1000.0
        #M = 7500.0
        #self.dLdt = M * C * np.cos(C * t)
        #self.L = self.L_init + M * np.sin(C * t)
        self.update_L(self.L)

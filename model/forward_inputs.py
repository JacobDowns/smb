from dolfin import *
import numpy as np
from common_inputs import *

"""
Standard forward model inputs.
"""

class ForwardInputs(CommonInputs):

    def __init__(self, input_file_name, adot_inputs, dt, N):

        super(ForwardInputs, self).__init__(input_file_name, adot_inputs)

        # Time Step
        self.dt = dt
        # Number of time steps to take
        self.N = N

from dolfin import *
import numpy as np
from common_inputs import *

"""
Replay forward inputs (replays an inverse model run in the forwrad model.)
"""

class ForwardInputsReplay(CommonInputs):

    def __init__(self, input_file_name, adot_inputs):

        super(ForwardInputsReplay, self).__init__(input_file_name, adot_inputs)

        # Number of steps
        self.N = self.input_file.attributes("adot0")['count']
        # Time step
        dt = Function(self.V_r)
        self.input_file.read(dt, "dt")
        self.dt = float(dt)
        # Free SMB parameter
        self.adot_param = Function(self.V_r)


    # Return the smb expression, just ignore the surface
    def get_adot_exp(self, S):
        return self.adot_inputs.get_adot_exp(S, self.adot_param)


    # Update inputs that change with length, iteration, time, and time step
    def update_inputs(self, i, t, L, dt):
        # Read in the SMB parameter
        self.input_file.read(self.adot_param, "adot0/vector_" + str(i))
        # Assign bed function
        self.bed_inputs.update(L)
        # Update adto expression
        self.adot_inputs.update(t, L)

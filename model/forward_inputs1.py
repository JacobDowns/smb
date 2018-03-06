from dolfin import *
from common_inputs1 import *

"""
Model inputs for the reverse model. This includes common inputs as well as glacier
length L.
"""

class ForwardInputs1(CommonInputs1):

    def __init__(self, input_file_name):

        super(ForwardInputs1, self).__init__(input_file_name)
        # SMB
        self.adot = Function(self.V_r)
        # Number of steps
        self.N = self.input_file.attributes("adot0")['count']
        # Time step
        dt = Function(self.V_r)
        self.input_file.read(dt, "dt")
        self.dt = float(dt)


    # Update iteration and length
    def assign_inputs(self, i, L):
        self.input_file.read(self.adot, "adot0/vector_" + str(i))

        self.B_exp.L = L
        self.beta2_exp.L = L

        self.B.interpolate(self.B_exp)
        self.beta2.interpolate(self.beta2_exp)


    def adot_expression(self, S):
        return super(ForwardInputs1, self).adot_expression(S, self.adot)

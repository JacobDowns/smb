from dolfin import *
from common_inputs_realistic import *

"""
Realistic inputs for the forward model.
"""

class ForwardInputsRealisticSteady(CommonInputsRealistic):

    def __init__(self, input_file_name):

        super(ForwardInputsRealistic, self).__init__(input_file_name)

        # Surface mass balance
        class Adot(Expression):
            def __init__(self, L_initial, degree=1):
                self.L = L_init
                self.degree=degree

            def eval(self, values, x):
                x = x[0]*self.L
                values[0] = adot_max*(1.0 - 2.0*(x / L_steady))




    # Update iteration and length
    def assign_inputs(self, i, L):
        self.assign_B(L)
        self.beta2.interpolate(self.beta2_exp)


    def adot_expression(self, S):
        return super(ForwardInputs1, self).adot_expression(S, self.adot)

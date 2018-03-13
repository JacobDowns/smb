from model.inverse_inputs import *
from model.length_inputs_linear import *
from model.adot_inputs_dependent import *
from model.inverse_model.inverse_ice_model import *

"""
Generate a steady state for IS using an elevation dependent SMB functions.
"""

adot_inputs = AdotInputsDependent(0.)
length_inputs = LengthInputsConstant()

inputs = InverseInputs('is_dependent_steady.hdf5', adot_inputs, length_inputs, dt = 2., N = 5000)
model = InverseIceModel(inputs, "out", "is_replay_steady_dependent")

while model.i < model.steps:
    print model.i
    model.step()

model.write_steady_file('is_dependent_steady')

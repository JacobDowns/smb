from model.inverse_inputs import *
from model.length_inputs_linear import *
from model.adot_inputs_elevation_dependent import *
from model.inverse_model.inverse_ice_model import *

"""
Generate a steady state for IS using an elevation dependent SMB functions.
"""

adot_inputs = AdotInputsElevationDependent()
length_inputs = LengthInputsLinear(0.)

inputs = InverseInputs('is_spatial_steady_width.hdf5', adot_inputs, length_inputs, dt = 2., N = 4000)
model = InverseIceModel(inputs, "out", "is_replay_steady_elevation_dependent_width")

S_func = Function(model.V_cg)

while model.i < model.steps:
    print model.i
    model.step()
    S_func.assign(project(model.S, model.V_cg))
    plot(S_func, interactive = False)
    plot(model.B, interactive = False)

model.write_steady_file('is_steady_elevation_dependent_width')

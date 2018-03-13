from model.inverse_inputs import *
from model.length_inputs_linear import *
from model.adot_inputs_elevation_dependent import *
from model.inverse_model.inverse_ice_model import *

"""
Force the ice sheet to retreat at a constant rate of speed.
"""

adot_inputs = AdotInputsElevationDependent()
length_inputs = LengthInputsLinear(-25.)

inputs = InverseInputs('is_steady_elevation_dependent.hdf5', adot_inputs, length_inputs, dt = 1., N = 6000)
model = InverseIceModel(inputs, "out", "is_replay_steady_elevation_dependent")

S_func = Function(model.V_cg)

while model.i < model.steps:
    print model.i
    model.step()
    S_func.assign(project(model.S, model.V_cg))
    plot(S_func, interactive = False)
    plot(model.B, interactive = False)

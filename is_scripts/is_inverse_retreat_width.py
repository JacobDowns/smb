from model.inverse_inputs import *
from model.length_inputs_linear import *
from model.adot_inputs_elevation_dependent import *
from model.inverse_model.inverse_ice_model import *
import matplotlib.pyplot as plt

"""
Force the ice sheet to retreat at a constant rate of speed.
"""

adot_inputs = AdotInputsElevationDependent()
length_inputs = LengthInputsLinear(-25.)

inputs = InverseInputs('is_steady_elevation_dependent_width.hdf5', adot_inputs, length_inputs, dt = 1., N = 6000)
model = InverseIceModel(inputs, "out", "is_replay_steady_elevation_dependent_width")

S_func = Function(model.V_cg)

# Stores value of smb param through time
adot_params = []
# Lengths
lengths = []

while model.i < model.steps:
    adot0, L = model.step()
    adot_params.append(adot0)
    lengths.append(L)

plt.plot(adot_params)
plt.show()

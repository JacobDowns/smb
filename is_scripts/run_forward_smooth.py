from model.forward_inputs_replay import *
from model.adot_inputs_elevation_dependent import *
from model.forward_model.forward_ice_model import *
import numpy as numpy
import matplotlib.pyplot as plt

"""
Force the ice sheet to retreat at a constant rate of speed.
"""

adot_inputs = AdotInputsElevationDependent()
inputs = ForwardInputsReplay('out/replay/is_replay_retreat_smooth_3001.hdf5', adot_inputs)
model = ForwardIceModel(inputs, "out", "forward_replay")
# Do this once, just so we can get the bed data
inputs.update_inputs(0, 0., inputs.L_init, 1.)

ts = []
Ls = []

while model.i < model.steps:
    ts.append(model.t)
    Ls.append(model.step())

ts = np.array(ts)
Ls = np.array(Ls)

#lt.plot(ts, Ls)
#plt.plot(ts, inputs.L_init - 25.*ts)

plt.plot(ts, (inputs.L_init - 25.*ts) - Ls, 'k', linewidth = 2)

plt.xlim(0., ts.max())
plt.xlabel('Time (years)')
plt.ylabel('Error (m)')

plt.show()

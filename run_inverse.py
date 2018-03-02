from model.inverse_inputs1 import *
from model.inverse_model.inverse_ice_model import *

inverse_inputs = InverseInputs1('steady_bumps.hdf5')
model = InverseIceModel(inverse_inputs, "out", "replay_bumps")
model.run(1., 6000)

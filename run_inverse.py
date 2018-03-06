from model.inverse_inputs1 import *
from model.inverse_model.inverse_ice_model import *

#inverse_inputs = InverseInputs1('steady_bumps.hdf5')
inverse_inputs = InverseInputs1('steady_dependent1.hdf5')
model = InverseIceModel(inverse_inputs, "out", "replay_dependent")
model.run(1., 6000)
#model.write_steady_file('steady_dependent1')

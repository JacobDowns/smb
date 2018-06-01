from model.inputs.forward_paleo_inputs import *
from model.forward_model.forward_ice_model import *
import matplotlib.pyplot as plt


model_inputs = ForwardPaleoInputs('paleo_inputs/is_smooth_steady.hdf5', dt = 0.5)
model = ForwardIceModel(model_inputs, "out", "paleo")

# Number of steps
N = 2750

ts = []
Ls = []

for i in range(N):
    ts.append(model_inputs.start_year + model.t)
    Ls.append(model.step())

model.write_steady_file('paleo_inputs/filter_start')

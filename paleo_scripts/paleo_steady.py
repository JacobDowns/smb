#from model.forward_inputs import *
from model.forward_model.forward_ice_model import *

"""
forward_inputs = ForwardInputs('out/replay_retreat.hdf5')
model = ForwardIceModel(forward_inputs, "out", "forward")

ts = []
Ls = []

while model.i < model.N:
    ts.append(model.t)
    Ls.append(float(model.L0))
    model.step()
    plot(model.H0)"""

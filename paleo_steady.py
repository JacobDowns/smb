from model.inputs.forward_paleo_inputs_steady import *
from model.forward_model.forward_ice_model import *
import matplotlib.pyplot as plt


model_inputs = ForwardPaleoInputsSteady('paleo_inputs/is_flowline_new.h5')
model = ForwardIceModel(model_inputs, "out", "paleo")

for i in range(2500):
    model.step()

dolfin.plot(model.S0_c)
plt.show()



"""
model = ForwardIceModel(forward_inputs, "out", "forward")

ts = []
Ls = []

while model.i < model.N:
    ts.append(model.t)
    Ls.append(float(model.L0))
    model.step()
    plot(model.H0)"""

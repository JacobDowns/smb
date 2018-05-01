from model.inputs.forward_paleo_inputs_steady import *
from model.forward_model.forward_ice_model import *
import matplotlib.pyplot as plt


model_inputs = ForwardPaleoInputsSteady('paleo_inputs/is1.h5', dt = 0.5)
model = ForwardIceModel(model_inputs, "out", "paleo")

for i in range(5000):
    model.step()

    if i % 100 == 0 or i == 341*2:
        dolfin.plot(model.S0_c)
        dolfin.plot(model.B)
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

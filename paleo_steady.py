from model.inputs.forward_paleo_inputs_steady import *
from model.forward_model.forward_ice_model import *
import matplotlib.pyplot as plt


model_inputs = ForwardPaleoInputsSteady('paleo_inputs/is_flowline_300.h5')
model = ForwardIceModel(model_inputs, "out", "paleo")

dolfin.plot(model_inputs.input_functions['B'] + model_inputs.input_functions['H0_c'])
print model_inputs.input_functions['H0_c'].vector().array()
quit()
#dolfin.plot(model_inputs.adot_)
#plt.show()


model.step()



"""
model = ForwardIceModel(forward_inputs, "out", "forward")

ts = []
Ls = []

while model.i < model.N:
    ts.append(model.t)
    Ls.append(float(model.L0))
    model.step()
    plot(model.H0)"""

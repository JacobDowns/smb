from model.inputs.forward_paleo_inputs_steady import *
from model.forward_model.forward_ice_model import *
import matplotlib.pyplot as plt

model_inputs = ForwardPaleoInputsSteady('paleo_inputs/is_paleo.h5', dt = 5.)
model = ForwardIceModel(model_inputs, "out", "paleo")

for i in range(25000):
    model.step()

dolfin.plot(model.B)
dolfin.plot(model.B + model.H0_c)
plt.ylim(-250., 3000.)
plt.show()

model.write_steady_file('paleo_inputs/is_paleo_steady')

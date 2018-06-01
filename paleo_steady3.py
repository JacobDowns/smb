from model.inputs.forward_paleo_inputs_steady import *
from model.forward_model.forward_ice_model import *
import matplotlib.pyplot as plt


#model_inputs = ForwardPaleoInputsSteady('paleo_inputs/is1.h5', dt = 2.)
model_inputs = ForwardPaleoInputsSteady('paleo_inputs/is3.h5', dt = 0.1)
model = ForwardIceModel(model_inputs, "out", "paleo")


dolfin.plot(model.S_f)
dolfin.plot(model.B)
plt.ylim([-500., 3000.])
plt.show()

for i in range(1000):
    model.step()

model.write_steady_file('paleo_inputs/is3_steady1')


dolfin.plot(model.S_f)
dolfin.plot(model.B)
plt.ylim([-500., 3000.])
plt.show()

from model.inputs.forward_paleo_inputs_steady import *
from model.forward_model.forward_ice_model import *
import matplotlib.pyplot as plt

model_inputs = ForwardPaleoInputsSteady('paleo_inputs/is_smooth.h5', dt = 2.)
model = ForwardIceModel(model_inputs, "out", "paleo")

for i in range(13000):
    model.step()
    #dolfin.plot(model.H0_c)
    dolfin.plot(model.adot_prime_func)
    plt.show()

plt.show()
model.write_steady_file('paleo_inputs/is_smooth_steady')

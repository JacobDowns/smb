from model.inputs.forward_paleo_inputs_steady import *
from model.forward_model.forward_ice_model import *
import matplotlib.pyplot as plt

model_inputs = ForwardPaleoInputsSteady('paleo_inputs/newthing1.hdf5', dt = 2.)
model = ForwardIceModel(model_inputs, "out", "paleo")

quit()
dolfin.plot(model.S_f)
dolfin.plot(model.B)
plt.show()

for i in range(1000):
    model.step()




#model.write_steady_file('paleo_inputs/is_new_steady3')



#dolfin.plot(model.S_f)
#dolfin.plot(model.B)
#plt.ylim([-250., 3000.])
#dolfin.plot(model.adot_prime_func)
#plt.show()

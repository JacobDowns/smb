from model.forward_inputs import *
from model.adot_inputs_linear import *
from model.forward_model.forward_ice_model import *
import matplotlib.pyplot as plt

adot_inputs = AdotInputsLinear(adot_max = 0.5, L_steady = 425e3)
#inputs = ForwardInputs('forward_inputs/is_inputs_new2.h5', adot_inputs, dt = 7.5, N = 4000)
inputs = ForwardInputs('forward_inputs/is_inputs_width.h5', adot_inputs, dt = 1., N = 4000)
model = ForwardIceModel(inputs, "out", "is_steady")

S_func = Function(model.V_cg)





while model.i < model.steps:
    model.step()
    S_func.assign(project(model.S, model.V_cg))


    dolfin.plot(model.un)
    plt.show()

model.write_steady_file('is_spatial_steady')

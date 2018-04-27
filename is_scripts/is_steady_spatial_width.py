from model.forward_inputs import *
from model.adot_inputs_linear import *
from model.forward_model.forward_ice_model import *

adot_inputs = AdotInputsLinear(adot_max = 0.5, L_steady = 397e3)
#inputs = ForwardInputs('forward_inputs/is_inputs_new2.h5', adot_inputs, dt = 7.5, N = 4000)
inputs = ForwardInputs('forward_inputs/is_inputs_width.h5', adot_inputs, dt = 10., N = 7500)
model = ForwardIceModel(inputs, "out", "is_steady_spatial_width")


S_func = Function(model.V_cg)

while model.i < model.steps:
    model.step()
    S_func.assign(project(model.S, model.V_cg))
    plot(S_func, interactive = False)
    #plot(model.width * model.adot_prime_func, interactive = True)
    print assemble(model.width * model.adot_prime_func * dx)
    #plot(, interactive = False)

model.write_steady_file('is_spatial_steady_width')

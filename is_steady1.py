from model.forward_inputs_realistic_steady import *
from model.forward_model.forward_ice_model import *

forward_inputs = ForwardInputsRealisticSteady('inputs/is_inputs.h5', dt = 2., N = 25000)



plot(forward_inputs.B, interactive = True)

"""
model = ForwardIceModel(forward_inputs, "out", "is_steady")

S_func = Function(model.V_cg)

while model.i < model.N:
    print model.i
    model.step()
    S_func.assign(project(model.S, model.V_cg))
    plot(S_func, interactive = False)

model.write_steady_file('is_spatial_steady')"""

from model.forward_inputs_replay import *
from model.adot_inputs_elevation_dependent import *
from model.forward_model.forward_ice_model import *

"""
Force the ice sheet to retreat at a constant rate of speed.
"""

adot_inputs = AdotInputsElevationDependent()
inputs = ForwardInputsReplay('out/replay/is_replay_retreat.hdf5', adot_inputs)
model = ForwardIceModel(inputs, "out", "forward_replay")
# Do this once, just so we can get the bed data
inputs.update_inputs(0, 0., inputs.L_init, 1.)

import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 22})

### Setup plot
################################################################################

plt.ion()
fig,ax = plt.subplots(nrows=2,sharex=True,figsize=(7,7))
xs = inputs.mesh.coordinates() * inputs.L_init

L_init = inputs.L_init

bed = project(model.B)
surface = project(model.S)
adot = project(model.adot_prime_func)
bed = project(inputs.B)

ph_bed, = ax[0].plot(xs, bed.compute_vertex_values(), 'b', linewidth = 2.5)
ph_surface, = ax[0].plot(xs, surface.compute_vertex_values(), 'k', linewidth = 2.5)
ph_term, = ax[0].plot([inputs.L_init, inputs.L_init], [-500., 4000.], 'r--', linewidth = 2.5)
ax[0].set_ylim(-400, 3500.)
ax[0].set_xlim(0, inputs.L_init)
ax[0].set_ylabel('H (m)')

ph_adot, = ax[1].plot(xs, adot.compute_vertex_values(), 'k', linewidth = 2.5)
ax[1].plot(xs, 0.*xs, 'b', linewidth = 2.5)
ax[1].set_ylim(-2.5, 1.5)
ax[1].set_xlim(0, inputs.L_init)
ax[1].set_xlabel('x (km)')
ax[1].set_ylabel('smb (m/a)')

plt.pause(0.00000001)

while model.i < model.steps:
    print model.i
    model.step()

    if model.i % 10 == 0:
        xs = inputs.mesh.coordinates() * float(model.L0)

        # Plot thickness
        surface = project(model.S)
        ph_surface.set_xdata(xs)
        ph_surface.set_ydata(surface.compute_vertex_values())

        # Plot smb
        #ax[1].set_xlim(0, float(model.L0))
        adot = project(model.adot_prime_func)
        ph_adot.set_xdata(xs)
        ph_adot.set_ydata(adot.compute_vertex_values())

        # Plot terminus line

        #L_opt = L_init - 25. * model.t
        L_opt = L_init -25.*model.t
        ph_term.set_xdata([L_opt, L_opt])
        ph_term.set_ydata([-550., 4000.])
        # Plot terminus line


        plt.pause(0.000000000000000001)

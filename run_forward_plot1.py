from model.forward_inputs1 import *
from model.forward_model.forward_ice_model import *

forward_inputs = ForwardInputs1('out/replay_bumps.hdf5')
model = ForwardIceModel(forward_inputs, "out", "forward")

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
plt.rcParams.update({'font.size': 22})

### Setup plot
################################################################################

#plt.ion()
fig,ax = plt.subplots(nrows=2,sharex=True,figsize=(10, 10))

lines = []

xs = forward_inputs.mesh.coordinates() * forward_inputs.L_init
xs_full = np.linspace(0., forward_inputs.L_init, 100)

L_init = forward_inputs.L_init

surface = project(model.S)
adot = project(model.adot)

ph_bed, = ax[0].plot(xs_full, 250.*np.cos(2.*np.pi*xs_full / 100000.) - 250.0, 'b', linewidth = 2.5)
ph_surface, = ax[0].plot(xs, surface.compute_vertex_values(), 'k', linewidth = 2.5)
ph_term, = ax[0].plot([forward_inputs.L_init, forward_inputs.L_init], [-100., 4000.], 'r--', linewidth = 2.5)
ax[0].set_title('Year 0')
ax[0].set_ylim(-550, 4000)
ax[0].set_xlim(0, forward_inputs.L_init)
ax[0].set_ylabel('H (m)')

ph_adot, = ax[1].plot(xs, adot.compute_vertex_values(), 'k', linewidth = 2.5)
ax[1].plot(xs_full, 0.0 * xs_full, 'b', linewidth = 2.5)
ax[1].set_ylim(-2.5, 1.5)
ax[1].set_xlim(0, forward_inputs.L_init)
ax[1].set_xlabel('x (km)')
ax[1].set_ylabel('smb (m/a)')

lines.append(ph_bed)
lines.append(ph_surface)
lines.append(ph_term)
lines.append(ph_adot)

def update(i):

    for i in range(20):
        model.step()

    xs = forward_inputs.mesh.coordinates() * float(model.L0)

    # Plot thickness
    surface = project(model.S)
    ph_surface.set_xdata(xs)
    ph_surface.set_ydata(surface.compute_vertex_values())

    # Plot smb
    #ax[1].set_xlim(0, float(model.L0))
    adot = project(model.adot)
    ph_adot.set_xdata(xs)
    ph_adot.set_ydata(adot.compute_vertex_values())

    # Plot terminus line
    L_opt = L_init - 25. * model.t
    ph_term.set_xdata([L_opt, L_opt])
    ph_term.set_ydata([-550., 4000.])

    ax[0].set_title('Year: ' + str(int(model.t)))

    return lines

#anim = animation.FuncAnimation(fig, animate, init_func=init,
#                               frames=100, interval=20, blit=True)

anim = animation.FuncAnimation(fig, update, frames=299, interval=1, blit = True)
anim.save('bumps.gif', dpi=100, writer='imagemagick')

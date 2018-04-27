import numpy as np
import matplotlib.pyplot as plt
import statsmodels.stats.api as sms

num_samples = 1025
years = 6000

font = {'size'   : 22}
plt.rc('font', **font)

fig, ax = plt.subplots()
fig.set_size_inches(0.5*11., 0.5*5.2)
ts = np.linspace(0., float(years), years)

length_mat = np.loadtxt('sample_lengths/lengths.txt')
num_samples = length_mat.shape[0]

ax.set_xlabel('Time (years)')
ax.set_ylabel('Length')

for i in range(10):
    ax.plot(ts, length_mat[i+20,:], lw = 2)

ax.set_xticks(np.linspace(0., 6000., 13))
ax.grid(linewidth=1)
fig.show()
fig.savefig('lengths.png', dpi = 300)

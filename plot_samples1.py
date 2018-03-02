import numpy as np
import matplotlib.pyplot as plt
import statsmodels.stats.api as sms

num_samples = 1025
years = 6000

font = {'size'   : 22}
plt.rc('font', **font)

fig, ax = plt.subplots()
fig.set_size_inches(11., 5.2)

ts = np.linspace(0., float(years), years)

#rate_mat = np.loadtxt('sample_rates/rates.txt')
length_mat = np.loadtxt('sample_lengths/lengths.txt')

for i in range(num_samples):
    print i
    ax.plot(ts, length_mat[i,:])

#fig.show()
fig.savefig('lengths.png', dpi = 300)

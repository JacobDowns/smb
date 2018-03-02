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

"""
rate_mat = np.zeros((num_samples, years))
length_mat = np.zeros((num_samples, years))


for i in range(num_samples):
    print i
    rates = np.loadtxt('sample_rates/' + str(i) + '.txt')
    lengths = np.loadtxt('sample_lengths/' + str(i) + '.txt')
    # Save the lapse rate in units of cm / (km a)
    rate_mat[i, :] = ((rates / lengths) * 1000.)
    length_mat[i, :] = lengths

np.savetxt('sample_rates/rates.txt', rate_mat)
np.savetxt('sample_lengths/lengths.txt', length_mat)

print rate_mat
print
print length_mat

quit()"""




rate_mat = np.loadtxt('sample_rates/rates.txt')
length_mat = np.loadtxt('sample_lengths/lengths.txt')

print rate_mat
print length_mat

import numpy as np, scipy.stats as st

"""
for i in range(num_samples):
    print i
    plt.plot(ts, rate_mat[i,:])"""

r_l = np.zeros(years)
r_u = np.zeros(years)
r_mean = np.zeros(years)

for i in range(years):
    print i

    rv = st.rv_discrete(values=(rate_mat[:,i], np.ones(num_samples) / float(num_samples)))

    r_mean[i] = rv.median()

    conf_int = rv.interval(0.95)
    r_l[i] = conf_int[0]
    r_u[i] = conf_int[1]

# scipy.stats.rv_discrete has methods for median, confidence interval, etc.
#print("median:", rv.median())
#print("68% CI:", rv.interval(0.68))

#print r_l
#print r_u

ax.set_title(r'Lapse rate $r$ for $\dot{a} = 1-rx$')
ax.set_xlabel('Time (years)')
ax.set_ylabel(r'Lapse rate ($\frac{m a^{-1} }{km}$)')

ax.plot(ts, r_l, 'b', lw = 2.75)
ax.plot(ts, r_u, 'b', lw = 2.75)
ax.plot(ts, r_mean, 'k', lw = 2.75)
fig.show()
#np.histogram([1, 2, 1], bins=[0, 1, 2, 3])

fig.savefig('rate.png', dpi = 300)

"""
#print r_mean

plt.plot(ts, r_mean, 'k', lw = 4)


plt.subplot(2,1,2)


xs = np.linspace(350e3, 500e3)
Bs = 250.*np.cos(2.*np.pi*xs / 100000.) - 250.0

plt.plot(xs, Bs)
plt.xlim([350e3, 500e3])
plt.show()"""

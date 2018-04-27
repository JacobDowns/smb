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
for i in range(num_samples):
    print i
    try :
        rates = np.loadtxt('sample_rates1/' + str(i) + '.txt')
        lengths = np.loadtxt('sample_lengths1/' + str(i) + '.txt')
        plt.plot(lengths)
    except:
        pass

plt.show()


rate_mat = np.zeros((num_samples, years))
length_mat = np.zeros((num_samples, years))

j = 0

for i in range(num_samples):

    try :
        print i
        rates = np.loadtxt('sample_rates1/' + str(i) + '.txt')
        lengths = np.loadtxt('sample_lengths1/' + str(i) + '.txt')

        # Save the lapse rate in units of cm / (km a)
        rate_mat[j, :] = rates
        length_mat[j, :] = lengths
        j += 1
    except :
        pass

print rate_mat[0:j,:]

np.savetxt('sample_rates1/rates.txt', rate_mat[0:j, :])
np.savetxt('sample_lengths1/lengths.txt', length_mat[0:j, :])

quit()

"""


rate_mat = np.loadtxt('sample_rates1/rates.txt')
length_mat = np.loadtxt('sample_lengths1/lengths.txt')

print rate_mat
print length_mat

import numpy as np, scipy.stats as st

#for i in range(num_samples):
#    print i
#    plt.plot(ts, rate_mat[i,:])

r_l = np.zeros(years)
r_u = np.zeros(years)
r_mean = np.zeros(years)

num_samples = rate_mat.shape[0]


for i in range(years):
    print i

    rv = st.rv_discrete(values=(rate_mat[:,i], np.ones(num_samples) / float(num_samples)))

    r_mean[i] = rv.median()

    conf_int = rv.interval(0.95)
    r_l[i] = conf_int[0]
    r_u[i] = conf_int[1]

    print conf_int, rv.median()

# scipy.stats.rv_discrete has methods for median, confidence interval, etc.
#print("median:", rv.median())
#print("68% CI:", rv.interval(0.68))

#print r_l
#print r_u

#ax.set_title(r'$r$')
ax.set_xlabel('Time (years)')
ax.set_ylabel('p')

ax.plot(ts, r_l, 'b', lw = 2.75)
ax.plot(ts, r_u, 'b', lw = 2.75)
ax.plot(ts, r_mean, 'k', lw = 2.75)
ax.plot(ts, rate_mat[0,:], 'r', lw = 2.75)
ax.set_xticks(np.linspace(0., 6000., 13))
ax.grid(linewidth=1)



#array([    0.,  1500.,  3000.,  4500.,  6000.])



fig.show()
fig.savefig('rate1.png', dpi = 300)

"""
#np.histogram([1, 2, 1], bins=[0, 1, 2, 3])





#print r_mean

plt.plot(ts, r_mean, 'k', lw = 4)


plt.subplot(2,1,2)


xs = np.linspace(350e3, 500e3)
Bs = 250.*np.cos(2.*np.pi*xs / 100000.) - 250.0

plt.plot(xs, Bs)
plt.xlim([350e3, 500e3])
plt.show()"""

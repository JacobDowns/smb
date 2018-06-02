import numpy as np
from pylab import *
from scipy.interpolate import interp1d

plt.rcParams.update({'font.size': 22})

### Plot margin position through time
#############################################################################

subplot(2,1,1)

# Morainge ages and positions
ages = np.array([-11.6, -10.2, -9.2, -8.2, -7.3])*1e3
Ls = [406878.12855486432, 396313.20004890749, 321224.04532276397, 292845.40895793668, 288562.44342502725]

# Jensen Dye-3
ts1 = np.loadtxt('is_paleo/jensen_ts.txt')
Ls1 = np.loadtxt('is_paleo/jensen_Ls.txt')
# Buizert Dye-3
ts2 = np.loadtxt('is_paleo/buizert_ts.txt')
Ls2 = np.loadtxt('is_paleo/buizert_Ls.txt')
# NGRIP
ts3 = np.loadtxt('is_paleo/ngrip_ts.txt')
Ls3 = np.loadtxt('is_paleo/ngrip_Ls.txt')
# Kalman
ts4 = np.loadtxt('is_paleo/k_ts.txt')
Ls4 = np.loadtxt('is_paleo/k_Ls.txt')

plot(ts1, Ls1, 'r', linewidth = 2, label = 'Jensen Dye-3')
plot(ts2, Ls2, 'k', linewidth = 2, label = 'Buizert Dye-3')
plot(ts3, Ls3, 'b', linewidth = 2, label = 'NGRIP')
plot(ts4, Ls4, 'g', linewidth = 2, label = 'K')
xlim(ts1.min(), ts1.max())

ylabel('Glacier Length')

plot(ages, Ls, 'ro', ms = 10)
legend(loc = 3)


### Plot delta temps.
########################################################################

subplot(2,1,2)

### Jensen DYE-3 delta temp.
data = np.loadtxt('jensen_dye3.txt')
# Years before present (2000)
years = data[:,0] - 2000.0
# Temps. in K
temps = data[:,1]
# Jensen interpolator
delta_temp_interp1 = interp1d(years, temps - temps[-1], kind = 'linear')

### Buizert DYE-3 delta temp.
data = np.loadtxt('buizert_dye3.txt')
years = -data[:,0][::-1]
temps = data[:,1][::-1]
# Jensen interpolator
delta_temp_interp2 = interp1d(years, temps - temps[-1], kind = 'linear')

### NGRIP deltatemp.
data = np.loadtxt('d180.csv')
years = data[:,0]
# Isotope concentration
d180 = data[:,1]
# Conversion to delta temp
dpermil = 2.4
temps = dpermil*(d180 + 34.83)
delta_temp_interp3 = interp1d(years, temps - temps[-1], kind = 'linear')

plot(ts1, delta_temp_interp1(ts1), 'r', linewidth = 2, label = 'Jensen Dye-3')
plot(ts2, delta_temp_interp2(ts1), 'k', linewidth = 2, label = 'Buizert Dye-3')
plot(ts3, delta_temp_interp3(ts1), 'b', linewidth = 2, label = 'NGRIP')
xlim(ts1.min(), ts1.max())
xlabel('Year Before Present')
ylabel(r'$\Delta T$')

legend(loc = 4)
show()





import numpy as np
from pylab import *
from scipy.interpolate import interp1d

plt.rcParams.update({'font.size': 22})

### Plot margin position through time
#############################################################################

subplot(3,1,1)

# Morainge ages and positions
ages = np.array([-11.6, -10.2, -9.2, -8.2, -7.3])*1e3
Ls = [406878.12855486432, 396313.20004890749, 321224.04532276397, 292845.40895793668, 288562.44342502725]

# Jensen Dye-3
ts1 = np.loadtxt('is_paleo/jensen_ts1.txt')
Ls1 = np.loadtxt('is_paleo/jensen_Ls1.txt')
# Buizert Dye-3
ts2 = np.loadtxt('is_paleo/buizert_ts1.txt')
Ls2 = np.loadtxt('is_paleo/buizert_Ls1.txt')
# NGRIP
ts3 = np.loadtxt('is_paleo/ngrip_ts1.txt')
Ls3 = np.loadtxt('is_paleo/ngrip_Ls1.txt')
# L for Kalman run 1 (L_obs variance 6000.0**2)
Ls4 = np.loadtxt('is_paleo/k_Ls1.txt')
# L for Kalman run 2 (L_obs variance 8000.0**2)
Ls5 = np.loadtxt('is_paleo/k_Ls2.txt')
# Time steps for Kalman runs
ts_kalman = -11.6e3 + np.array(range(len(Ls4)))*(1./3.)


plot(ts1, Ls1, 'r', linewidth = 2, label = 'Jensen Dye-3')
plot(ts2, Ls2, 'k', linewidth = 2, label = 'Buizert Dye-3')
plot(ts3, Ls3, 'b', linewidth = 2, label = 'NGRIP')
plot(ts_kalman, Ls4, 'g', linewidth = 2, label = r'UKF $\sigma^2 = 6000^2$ ')
plot(ts_kalman, Ls5, 'y', linewidth = 2, label = r'UKF $\sigma^2 = 8000^2$ ')
xlim(ts1.min(), ts1.max())
ylabel('Glacier Length')
plot(ages, Ls, 'ro', ms = 10)
legend(loc = 3)


### Plot delta temps.
########################################################################

subplot(3,1,2)

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

k_delta_temps1 = np.loadtxt('is_paleo/k_delta_temps1.txt')
k_delta_temps2 = np.loadtxt('is_paleo/k_delta_temps2.txt')

plot(ts1, delta_temp_interp1(ts1), 'r', linewidth = 2, label = 'Jensen Dye-3')
plot(ts1, delta_temp_interp2(ts1), 'k', linewidth = 2, label = 'Buizert Dye-3')
plot(ts3, delta_temp_interp3(ts1), 'b', linewidth = 2, label = 'NGRIP')
plot(ts_kalman, k_delta_temps1, 'g', linewidth = 2, label = r'UKF $\sigma^2 = 6000^2$')
plot(ts_kalman, k_delta_temps2, 'y', linewidth = 2, label = r'UKF $\sigma^2 = 8000^2$')
ylabel(r'$\Delta T$')
xlim(ts1.min(), ts1.max())
legend(loc = 4)

subplot(3,1,3)

adot_ints_buizert = np.loadtxt('is_paleo/buizert_adot_int1.txt')
adot_ints_kalman = np.loadtxt('is_paleo/k_adot_ints1.txt')

plot(ts2, adot_ints_buizert, 'k', linewidth = 2, label = 'Buizert Dye-3')
plot(ts_kalman, adot_ints_kalman, 'g', linewidth = 2, label = r'UKF $\sigma^2 = 6000^2$')
ylabel('Avg. SMB (m/a)')
xlabel('Year Before Present')
xlim(ts1.min(), ts1.max())
legend(loc = 3)
show()





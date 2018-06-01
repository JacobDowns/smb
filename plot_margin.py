import matplotlib.pyplot as plt
import numpy as np

ts1 = np.loadtxt('is_paleo/jensen_ts.txt')
Ls1 = np.loadtxt('is_paleo/jensen_Ls.txt')

ts2 = np.loadtxt('is_paleo/buizert_ts.txt')
Ls2 = np.loadtxt('is_paleo/buizert_Ls.txt')

plt.plot(ts1, Ls1, 'ko-', ms = 2)
plt.plot(ts2, Ls2, 'ro-', ms = 2)
plt.xlim([ts.min(), ts.max()])
plt.ylim([500e3, 200e3])

plt.plot([-11.6e3, -11.6e3], [-1e10, 1e10], 'k-')
plt.plot([-10.3e3, -10.3e3], [-1e10, 1e10], 'k-')
plt.plot([-9.08e3, -9.08e3], [-1e10, 1e10], 'k-')
plt.plot([-8.13e3, -8.13e3], [-1e10, 1e10], 'k-')
plt.plot([-7.31e3, -7.31e3], [-1e10, 1e10], 'k-')
plt.show()

# Scirpt for plotting the results of the sensitivity analysis

import matplotlib.pyplot as plt
import numpy as np

# Pad = 3
rr = np.array([2, 3, 4, 5])
ops_tt6 = np.array([118, 132, 141, 144])
ops_tt8 = np.array([118, 132, 139, 142])
ops_tt10 = np.array([119, 132, 138, 140])

fs = 16
fig, ax = plt.subplots()
ax.plot(rr, ops_tt6, 'r-', marker='.', label='Turnaround Time = 6 min', linewidth=2.0)
ax.plot(rr, ops_tt8, 'g-', marker='.', label='Turnaround Time = 8 min', linewidth=2.0)
ax.plot(rr, ops_tt10, 'b-', marker='.', label='Turnaround Time = 10 min', linewidth=2.0)
ax.grid()
ax.set_xlabel('Recharge Rate (units/min)', fontsize=fs)
ax.set_ylabel('Total touchdown & liftoff', fontsize=fs)
ax.legend(fontsize=fs-2, loc='lower right')
plt.xticks(rr,fontsize=fs-2)
plt.yticks(fontsize=fs-2)
plt.tight_layout()
# plt.show()
plt.savefig('sens_rr_pad3.pdf', dpi=300)

# Pad = 4
rr = np.array([2, 3, 4, 5])
ops_tt6 = np.array([121, 132, 141, 144])
ops_tt8 = np.array([121, 132, 139, 142])
ops_tt10 = np.array([121, 132, 139, 140])

fs = 16
fig, ax = plt.subplots()
ax.plot(rr, ops_tt6, 'r-', marker='.', label='Turnaround Time = 6 min', linewidth=2.0)
ax.plot(rr, ops_tt8, 'g-', marker='.', label='Turnaround Time = 8 min', linewidth=2.0)
ax.plot(rr, ops_tt10, 'b-', marker='.', label='Turnaround Time = 10 min', linewidth=2.0)
ax.grid()
ax.set_xlabel('Recharge Rate (units/min)', fontsize=fs)
ax.set_ylabel('Total touchdown & liftoff', fontsize=fs)
ax.legend(fontsize=fs-2, loc='lower right')
plt.xticks(rr,fontsize=fs-2)
plt.yticks(fontsize=fs-2)
plt.tight_layout()
# plt.show()
plt.savefig('sens_rr_pad4.pdf', dpi=300)


import numpy as np

# fishing line stiffness
k_fl = 117.54e3 / 1000. # N/mm
# print(f"Fishing line stiffness: {k_fl} N/mm")

L = 52.57e-3 # m
A = np.pi * (6.30e-3)**2 / 4. / 2. # m**2

# aluminum stiffness
E_Al = 69.e9 # Pa or N/m**2
k_Al = E_Al * A / L / 1000. # N/mm
# print(f"Aluminum stiffness: {k_Al} N/mm")

# PLA stiffness
E_PLA = 2580.e6 # Pa or N/m**2
k_PLA = E_PLA * A / L / 1000. # N/mm
# print(f"PLA stiffness: {k_PLA} N/mm")
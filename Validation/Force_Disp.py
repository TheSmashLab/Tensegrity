'''
This module reads the force-displacement data from a CSV file and converts it to the appropriate units for comparison with the tendon model.
The CSV file is expected to have two columns: "Displacement" (in mm) and "Force" (in N).
The function `force_disp` reads the data, converts the units, and returns the displacement and force as numpy arrays.
'''

import csv
import numpy as np

def force_disp(filename):
    Disp = []  # displacement in mm
    Force = []  # force in N
    with open(filename, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        next(reader)
        for row in reader:
            Disp.append(float(row["Displacement"]))  # mm
            Force.append(float(row["Force"]))  # N
    # convert sheet units to tendon units
    Disp = np.array(Disp) / 100. * 68.12  # mm
    Force = np.array(Force) / 1. * 1.2 ** 2  # N
    # return as numpy arrays
    return np.array(Disp), np.array(Force)
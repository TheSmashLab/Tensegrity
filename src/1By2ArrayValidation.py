"""
Validation of the 1-by-2 array tensegrity structure.
This script sets up a 1-by-2 array tensegrity structure with specific node positions,
connections, and material properties. It then solves the system using the TensegritySolver
and visualizes the results.
"""

# import libraries
import csv
import numpy as np
from matplotlib import pyplot as plt
from TensegritySim import Node, Connection, Tensegrity
from TensegritySim import TensegritySolver, Visualization
import argparse

# Experimental Positions
x_pos = []
y_pos = []
with open("Tables/Array 18 1by2.csv", "r", newline="") as posfile:
    reader = csv.DictReader(posfile)
    for row in reader:
        x_pos.append(float(row["Node 6 x"])) # mm
        y_pos.append(float(row["Node 6 y"])) # mm

plt.ion() # turns on iteractive mode
fig, ax = plt.subplots()
line, = ax.plot([], [], color="b") # creates an empty line object

ax.set_title(f"Position of Node 6")
ax.grid(True)

for i in range(1, len(x_pos)):
    line.set_data(x_pos[:i+1], y_pos[:i+1])
    plt.pause(1.0) # pause between updates (in seconds)

plt.ioff()
plt.show()
plt.close()

# shortcuts
string = Connection.ConnectionType.STRING
bar = Connection.ConnectionType.BAR

# fishing line stiffness
k_fl = 117.54e3 * 1000 # N/mm

# Stress-strain data for Bambu TPU
Strain = []
Stress = []
with open("Tables/Array_18_Table.csv", "r", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        Strain.append(float(row["Strain"])) # %
        Stress.append(float(row["Stress (MPa)"])) # MPa
Strain = np.array(Strain)
Stress = np.array(Stress)

# linear approximation for k_TPU
length = 65. # mm, gauge length
area = 1.2 * 1.2 # mm**2, cross-sectional area
displacement = Strain * length # mm
force = Stress * area # N

num_points = 1201 # best number found from 1 by 1 data
slope, intercept = np.polyfit(displacement[:num_points+1], force[:num_points+1], 1)
# y_pred = slope * displacement + intercept
k_TPU = slope # N/mm
print(f"TPU stiffness: {k_TPU:.2f} N/mm")
x = 650e-3 * 9.8 / k_TPU # mm, displacement
print(f"displacement: {x:.2f} mm")

# aluminum stiffness
E = 69e9 # Pa
L = 71e-3 # m
A = np.pi * (6.30e-3)**2 / 4 / 2 # m**2
k_Al = E * A / L * 1000 # N/mm

node1 = Node(name="A", position=np.array([0., 0.])) # mm
node2 = Node(name="B", position=np.array([68.12, 0.])) # mm
node3 = Node(name="C", position=np.array([68.12, 68.12])) # mm
node4 = Node(name="D", position=np.array([0., 68.12])) # mm
node5 = Node(name="E", position=np.array([136.24, 0.])) # mm
node6 = Node(name="F", position=np.array([136.24, 68.12])) # mm
nodes = [node1, node2, node3, node4, node5, node6]

connection1 = Connection(nodes=[node1, node2, node5, node6], connection_type=string, stiffness=k_fl, name="control_string")
connection2 = Connection(nodes=[node2, node3], connection_type=string, stiffness=k_TPU)
connection3 = Connection(nodes=[node3, node4], connection_type=string, stiffness=k_TPU)
connection4 = Connection(nodes=[node4, node1], connection_type=string, stiffness=k_TPU)
connection5 = Connection(nodes=[node3, node6], connection_type=string, stiffness=k_TPU)
connection6 = Connection(nodes=[node1, node3], connection_type=bar, stiffness=k_Al)
connection7 = Connection(nodes=[node2, node4], connection_type=bar, stiffness=k_Al)
connection8 = Connection(nodes=[node2, node6], connection_type=bar, stiffness=k_Al)
connection9 = Connection(nodes=[node5, node3], connection_type=bar, stiffness=k_Al)
connections = [connection1,
               connection2, connection3, connection4, connection5,
               connection6, connection7, connection8, connection9]

pins = {"A": [True, True],
        "B": [False, True],
        "C": [False, False],
        "D": [False, False],
        "E": [False, False],
        "F": [False, False]}

controls = [connection1]

# Create the tensegrity object
tensegrity_system = Tensegrity(nodes, connections, pins, controls)

# Create the visualization object
viz = Visualization(tensegrity_system)

# Plot the initial tensegrity system
viz.plot(label_nodes=True, label_connections=True)

# Solve the tensegrity system
solver = TensegritySolver(tensegrity_system)
solver.solve()

viz.plot(label_nodes=True, label_connections=True)

show_forces = False

print("Enter 'q' to quit.")
print("Enter 'r' to reset control lengths.")
print("Enter 'f' to show/hide forces.")
if len(tensegrity_system.controls) == 1:
    print(f"Enter changes in length to control {tensegrity_system.get_control_order()} to update simulation.")
else:
    print(f"Enter changes in length to control strings as comma-separated values in the order of: {tensegrity_system.get_control_order()} to update simulation.")

while True:
    user_input = input("Input: ")
    if user_input == "q":
        break
    elif user_input == "r":
        tensegrity_system.reset_control_lengths()
    elif user_input == "f":
        show_forces = not show_forces
        viz.plot(label_nodes=True, label_connections=True, label_forces=show_forces)
        continue
    else:
        delta_lengths = user_input.split(",")
        delta_lengths = [float(delta) for delta in delta_lengths]
        tensegrity_system.change_control_lengths(*delta_lengths)

    solver.solve()
    viz.plot(label_nodes=True, label_connections=True, label_forces=show_forces)

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="2D Tensegrity Simulator")
#     parser.add_argument("filename", help="YAML file to load", default="yaml/1-box.yaml")

#     args = vars(parser.parse_args())
#     main(file=args["filename"])
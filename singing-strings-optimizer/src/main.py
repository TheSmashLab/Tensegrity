import argparse
from scipy.optimize import minimize
import numpy as np
import matplotlib.pyplot as plt

from TensegritySim import YamlParser, TensegritySolver, Connection
from TensegritySim import Visualization as Viz

import time

# Global list to store the objective values
objective_vals = []
last_delta_x = []



def change_lengths(delta_x,init_lengths, solver):

    for i, connections in enumerate(solver.tensegrity.connections):
        connections.initial_length = init_lengths[i] + delta_x[i]

    return # it changes the lengths internally

def f(delta_x, solver, initial_lengths, target):
    # print(delta_x)
    # changing each string length directly, make sure the 
    change_lengths(delta_x, initial_lengths, solver)

    solver.solve()

    tensegrity_system = solver.tensegrity

    F = np.zeros(len(tensegrity_system.connections))
    for indx, connection in enumerate(tensegrity_system.connections):
        # print(connection.name)
        F[indx] = connection.force

    # print(F)
    num_bars = len(tensegrity_system.nodes)//2


    total = 0
    to_optimize = 6 # how many of the strings you want in equal tension, 0 means all of them
    for i in range(num_bars-1 + to_optimize, len(F)):
        total += (F[i] - target) ** 2
    # # apply penalty if needs be
    # if penalty_active == 1:
    #     total = total * 5

    objective_vals.append(total)
    last_delta_x.append(delta_x)
    return total


def main(file, freq_file):
    # Load the tensegrity system from the YAML file
    tensegrity_system = YamlParser.parse(file)

    string_connections = [connection for connection in tensegrity_system.connections if connection.connection_type == Connection.ConnectionType.STRING]
    
    # ----------------- Set up the tensegrity object -----------------
    # add linear density property to the connections (YOU CAN ADD CUSTOM PROPERTIES TO THE CONNECTIONS)
    for string in string_connections:
        if string.connection_type == Connection.ConnectionType.STRING:
            string.linear_density = 0.001589119542 #Kg/m
    
    # initial_frequencies = [616, 612, 530, 650, 664, 677]
    initial_frequencies = []
    # you could read these from a file, for instance:
    with open(freq_file, 'r') as file:
        initial_frequencies = [float(line.strip()) for line in file]
        file.close()

    # Override the initial_length of each connection based on the initial frequencies
    for i, string in enumerate(string_connections):
        current_length = string.current_length()
        string.force = (initial_frequencies[i] * 2 * current_length)**2 * string.linear_density
        string.initial_length = current_length - string.force / string.stiffness
    # ----------------------------------------------------------------

    
    # Create the visualization object
    
    viz = Viz(tensegrity_system)


    # Plot the initial tensegrity system

    # Solve the tensegrity system

    """Here goes an optimizer to find the needed changes in string length to acheive equal tension in the structure. 
    
    At each iteration the unstretched length of the bars should be updated, curently stored as self.initial_length in the data_structures,
    connections class. this should update the tensegrity class created by the yaml parser and plug it back into the 'optimizer' function
    to solve, put inthe objective function and make it stop when its converged."""
    viz.plot(label_nodes=False, label_connections=False, label_forces=False)
    
    input('Press enter to continue')
    start_time = time.time()
    
    # run an initial case with the setup from YAML file
    solver = TensegritySolver(tensegrity_system)
    solver.solve()

    # get the initial lengths of the strings

    

    F = np.zeros(len(tensegrity_system.connections))
    initial_lengths = np.zeros(len(tensegrity_system.connections))
    for indx, string in enumerate(tensegrity_system.connections):
        print(string.name)
        initial_lengths[indx] = solver.tensegrity.connections[indx].initial_length
        F[indx] = string.force

    initial_guess =np.zeros(len(tensegrity_system.connections)) # this will include the bars, just make sure their lengths never get changed
    # F = tensegrity_system
    # create bounds so the optimizer never tries to change the length of the bars
    # the number of bars is assumed to be the # of nodes/2, and its assumed bars are the first connections in tensegrity_system.connections
    bounds = [(0, 0)] * (len(tensegrity_system.nodes)//2) + [(None, None)] * (len(tensegrity_system.connections) - (len(tensegrity_system.nodes)//2))
    # set the target beforehand so it doesn't keep changing at every iteration
    target = 1 / (len(F) - 3) * sum(F[j] for j in range(3,len(F)))
    
    result = minimize(f, initial_guess, method='Nelder-Mead', args= (solver, initial_lengths, target), bounds=bounds)
    end_time = time.time()
    print(result)
    for indx, string in enumerate(solver.tensegrity.connections):
        print(f'{string.name} has a length of {string.initial_length:.2f} and a force of {string.force:.2f}')


    fig, ax = plt.subplots()
    print('last delta_x =')
    print(last_delta_x[-1])
    
    print('run time =' + str(end_time - start_time))

    ax.plot(objective_vals)
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Objective Function Value')
    ax.set_title('Objective Function Progress Over Iterations')
    fig.show()
    input('Press enter to continue')

    viz.plot(label_nodes=False, label_connections=False, label_forces=False)
    input('Press enter to continue')
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='2D Tensegrity Simulator')
    parser.add_argument("filename", nargs='?', default="3Bar.yaml", help="YAML file to load")
    parser.add_argument("freq_file", nargs='?', default="frequencies.txt", help="Frequencies file to load")

    args = vars(parser.parse_args())
    main(file=args["filename"], freq_file=args["freq_file"])





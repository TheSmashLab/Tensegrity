# This is the project for optimization

from scipy.optimize import minimize
import numpy as np
import matplotlib.pyplot as plt
import time

global convergence
convergence = []
global xyz_coords
xyz_coords = []


# def plot_and_save(points_list):
#     xlim = (-1, 4)  # Set the x-axis limits
#     ylim = (-1, 4)  # Set the y-axis limits
#     zlim = (-1, 4)  # Set the z-axis limits

#     for idx, points in enumerate(points_list):
#         fig = plt.figure()
#         ax = fig.add_subplot(111, projection='3d')

#         # Extract x, y, z coordinates for each point
#         x_coords = points[0]
#         y_coords = points[1]
#         z_coords = points[2]

#         # Plot the points
#         ax.scatter(x_coords, y_coords, z_coords, c='r', marker='o')

#         # Add lines between the points with customizable styling
#         lines = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 5), (0, 4), (1, 5), (2, 3), (4, 3), (4, 5),
#                  (5, 3)]  # Specify which points are connected
#         line_styles = [{'linewidth': 3, 'color': 'blue'},  # Customize line styles for each connection
#                        {'linewidth': 3, 'color': 'blue'},
#                        {'linewidth': 3, 'color': 'blue'},
#                        {'linewidth': 3, 'color': 'blue'},
#                        {'linewidth': 3, 'color': 'blue'},
#                        {'linewidth': 3, 'color': 'blue'},
#                        {'linewidth': 3, 'color': 'green'},
#                        {'linewidth': 3, 'color': 'green'},
#                        {'linewidth': 3, 'color': 'green'},
#                        {'linewidth': 3, 'color': 'black'},
#                        {'linewidth': 3, 'color': 'black'},
#                        {'linewidth': 3, 'color': 'black'}]

#         for line, style in zip(lines, line_styles):
#             ax.plot([x_coords[line[0]], x_coords[line[1]]],
#                     [y_coords[line[0]], y_coords[line[1]]],
#                     [z_coords[line[0]], z_coords[line[1]]],
#                     **style)

#         # Set axis labels
#         ax.set_xlabel('X')
#         ax.set_ylabel('Y')
#         ax.set_zlabel('Z')

#         # Set title
#         # ax.set_title(f'Plot {idx + 1}')

#         # Set axis limits
#         ax.set_xlim(xlim)
#         ax.set_ylim(ylim)
#         ax.set_zlim(zlim)

#         # Save figure as PNG
#         fig_path = f'figure_{idx + 1}.png'
#         plt.savefig(fig_path)
#         plt.close()

#         # print(f"Figure {idx + 1} saved as {fig_path}")

    # # Combine PNGs into video
    # input_directory = '.'  # Change this to the directory containing your PNGs
    # output_video = 'output_video.mp4'  # Change this to the desired output video file path
    # command = f"ffmpeg -framerate 1 -pattern_type glob -i '{input_directory}/figure_*.png' -c:v libx264 -pix_fmt yuv420p {output_video}"
    # subprocess.call(command, shell=True)
    # print(f"Video saved to: {output_video}")

    # # Delete PNG files
    # for file_name in os.listdir(input_directory):
    #     if file_name.startswith('figure_') and file_name.endswith('.png'):
    #         os.remove(os.path.join(input_directory, file_name))
    #         # print(f"Deleted {file_name}")

    # last_xcoords = points_list[-1][0]
    # last_ycoords = points_list[-1][1]
    # last_zcoords = points_list[-1][2]
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # j = 30
    # while j < 360:
    #     ax.cla()  # Clear previous plot
    #     ax.scatter(last_xcoords, last_ycoords, last_zcoords, c='r', marker='o')
    #     lines = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 5), (0, 4), (1, 5), (2, 3), (4, 3), (4, 5), (5, 3)]
    #     line_styles = [{'linewidth': 3, 'color': 'blue'}, {'linewidth': 3, 'color': 'blue'},
    #                    {'linewidth': 3, 'color': 'blue'},
    #                    {'linewidth': 3, 'color': 'blue'}, {'linewidth': 3, 'color': 'blue'},
    #                    {'linewidth': 3, 'color': 'blue'},
    #                    {'linewidth': 3, 'color': 'green'}, {'linewidth': 3, 'color': 'green'},
    #                    {'linewidth': 3, 'color': 'green'},
    #                    {'linewidth': 3, 'color': 'black'}, {'linewidth': 3, 'color': 'black'},
    #                    {'linewidth': 3, 'color': 'black'}]
    #     for line, style in zip(lines, line_styles):
    #         ax.plot([last_xcoords[line[0]], last_xcoords[line[1]]],
    #                 [last_ycoords[line[0]], last_ycoords[line[1]]],
    #                 [last_zcoords[line[0]], last_zcoords[line[1]]],
    #                 **style)
    #     ax.view_init(elev=20, azim=j)
    #     plt.pause(0.001)  # Pause to update the plot
    #     fig_path = f'figure_{j + 1}.png'
    #     plt.savefig(fig_path)
    #     # print(f"Figure {idx + 1}_{j + 1} saved as {fig_path}")
    #     j += 1
    # plt.show()
    # # Combine PNGs into video
    # input_directory = '.'  # Change this to the directory containing your PNGs
    # output_video = 'spinning.mp4'  # Change this to the desired output video file path
    # command = f"ffmpeg -framerate 1 -pattern_type glob -i '{input_directory}/figure_*.png' -c:v libx264 -pix_fmt yuv420p {output_video}"
    # subprocess.call(command, shell=True)
    # print(f"Video saved to: {output_video}")

    # # Delete PNG files
    # for file_name in os.listdir(input_directory):
    #     if file_name.startswith('figure_') and file_name.endswith('.png'):
    #         os.remove(os.path.join(input_directory, file_name))
    #         # print(f"Deleted {file_name}")


def Distances(positions):
    l = 0.14  # length at base
    # l = 2

    node4 = np.array([0, 0, 0])
    node5 = np.array([l, 0, 0])
    node6 = np.array([0.5 * l, l * 0.866, 0])
    # Extract x, y, z components for each node
    node1_x, node1_y, node1_z = positions[0][:3]
    node2_x, node2_y, node2_z = positions[1][:3]
    node3_x, node3_y, node3_z = positions[2][:3]

    # Store the components under variables of node names
    node1 = np.array([node1_x, node1_y, node1_z])
    node2 = np.array([node2_x, node2_y, node2_z])
    node3 = np.array([node3_x, node3_y, node3_z])

    len_stringA = (((node1[0] - node2[0]) ** 2 + (node1[1] - node2[1]) ** 2 + (node1[2] - node2[2]) ** 2) ** 0.5)
    len_stringB = (((node3[0] - node2[0]) ** 2 + (node3[1] - node2[1]) ** 2 + (node3[2] - node2[2]) ** 2) ** 0.5)
    len_stringD = (((node1[0] - node4[0]) ** 2 + (node1[1] - node4[1]) ** 2 + (node1[2] - node4[2]) ** 2) ** 0.5)
    len_stringE = (((node5[0] - node2[0]) ** 2 + (node5[1] - node2[1]) ** 2 + (node5[2] - node2[2]) ** 2) ** 0.5)
    len_stringF = (((node6[0] - node3[0]) ** 2 + (node6[1] - node3[1]) ** 2 + (node6[2] - node3[2]) ** 2) ** 0.5)
    len_stringC = (((node1[0] - node3[0]) ** 2 + (node1[1] - node3[1]) ** 2 + (node1[2] - node3[2]) ** 2) ** 0.5)

    lengths = [len_stringA, len_stringB, len_stringC, len_stringD, len_stringE, len_stringF]
    return lengths


# fitness function below
# do we need to add initial length x the x vectors???


def f(delta_x):
    """ These inital positions and forces are measured from the physical model"""
    ## find init_x from frequency equation
    k = 40  # define the stiffness of the cables
    # lin_dens = # define the linear density of your string
    # freq = [] # define the initial frequencies of all your strings
    # init_stretched = # measured distance between nodes, never changes
    # Force = (freq*2*init_stretched_x)**2*lin_dens #  find the forces on each cable at your starting positions
    # init_unstretched = init_stretched_x - Force/k # use these values to find the initial unstrethced lenghts of each of our cables

    """Or since we don't have a physical model yet run MOTES once and plug in these values by hand"""
    initial_Stretched = np.array(
        [0.12, 0.12, 0.12, 0.24, 0.24,
         0.24, .14, .14, .14])
    init_unstretched_x = np.array([.10, .10, .10, .13, .13, .13, .10, .10, # this is an array of all the initial unstretched lenghts of the cables
                                   .10])  # 0.7 * initial_Stretched # an array of the initial lengths of all the strings

    unstretched_lengths = delta_x + init_unstretched_x # delta x being the change in length of each string you attempt to get equiliibrium
    percents = np.divide(unstretched_lengths, initial_Stretched) #you need to find the percent stretch now to input to motes

    percents = percents.tolist()
    # print(percents)
    positions = Model(percents)  # got to the model function and input the initial conditions for your model before running this

    global xyz_coords
    global convergence
    xyz_coords.append(positions)

    stretched_x = Distances(positions)
    # add penalty if the algorithm is trying to shorten the strings too much
    # make sure the string is being changed way too much
    penalty_active = 0
    if np.max(delta_x) > 0.25 * initial_Stretched[np.argmax(delta_x)]:
        print('The biggest change is: ', np.max(delta_x))
        penalty_active = 1

    stretched_x = np.append(stretched_x, [2, 2, 2])

    # find new stretched_x from new node positions

    F = k * (stretched_x - unstretched_lengths)
    # print('THE FORCES: ', F)




    total = 0
    target = 1 / (len(F) - 3) * sum(F[j] for j in range(len(F) - 3))
    for i in range(len(F) - 3):
        total += (F[i] - target) ** 2
    # apply penalty if needs be
    if penalty_active == 1:
        total = total * 5

    convergence.append(total)
    return total


# deltax = np.array([.1,.2,.1,.1,.1,.2,0,0,0]) # insert the changes in string length, the last three should always be 0
# res = f(deltax)
# print(res)

x_lower = -1
x_upper = 1
initial_guess = [0, 0, 0, 0, 0, 0, 0, 0, 0]
start_time = time.time()
value = minimize(f, initial_guess, method='Nelder-Mead')
end_time = time.time()

# Calculate the elapsed time
elapsed_time = end_time - start_time

print("Wall time:", elapsed_time, "seconds")

# plot_and_save(xyz_coords) # make the figures
# print(bestpoint)
print(value)

indexes_list = [i for i in range(len(convergence))]
plt.figure()
plt.title('Convergence of 3-Bar Tensegrity')
plt.xlabel('Iterations')
plt.ylabel('Objective Func. Value')
plt.scatter(indexes_list, convergence)  # plot the convergence
plt.show()

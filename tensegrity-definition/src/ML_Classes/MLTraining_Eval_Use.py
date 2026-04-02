"""This file is to be used as a class to store ML training, eval, and future use information.
    This is the file that will pull together the linear network, the data, and then train it to predict the deltas for the
    system."""
"""tips from Taylor:
  3. learn the deltas, not the positions.  Makes the model more robust over wide input range.
  4. maybe use an RNN, previous information could help in the algorithm for some reason, but start vanilla."""

import torch
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from src.ML_Classes import MLLinearNetwork, MLDataImportAndCleaning
from src.TensegritySystem import Nodes as N
import cv2
import os


# Needs to be corrected for the datasets. So need datasets to be created before I can get much farther.
class trainMethod():
    def __init__(self, system, dt=.001, tf=5):
        self.system = system
        self.dt = dt
        self.axisLength = 3
        self.tf = tf
        self.dataSet = MLDataImportAndCleaning.DataImport()
        self.dataset, self.targets = self.dataSet.importData()  # should use this to also create validation dataset, maybe just random or symmetric sample?
        self.train_dataset = self.dataset[0:int(len(self.dataset) * .8)].float()
        # to 'batch' the data, made an artificial skip where it skips the first 3 time steps of each new try, which makes it so the program doesn't have weird previous state info in transition.

        self.train_targets = self.targets[0:int(len(self.targets) * .8)]
        self.train_targets = self.train_targets[:, :int(len(self.train_targets[0]) * 2 / 3)].float()

        self.val_dataset = self.dataset[int(len(self.dataset) * .8) + 4: int(len(self.dataset) * .9)].float()
        self.val_targets = self.targets[int(len(self.targets) * .8) + 4: int(len(self.targets) * .9)]
        self.val_targets = self.val_targets[:, :int(len(self.val_targets[0]) * 2 / 3)].float()

        self.test_dataset = self.dataset[int(len(self.dataset) * .9) + 4:].float()
        self.test_targets = self.targets[int(len(self.targets) * .9) + 4:]
        self.test_targets = self.test_targets[:, :int(len(self.test_targets[0]) * 2 / 3)].float()

        # Instantiate your model and loss and optimizer functions
        self.model = MLLinearNetwork.LinearNetwork(self.train_dataset).cuda()

        # saves the node history of the test model, used to make the animation at the end of the testing.
        self.nodeHist = np.array([[]])


    def train(self):
        # Needs to be corrected for the datasets. So need datasets to be created before I can get much farther.

        optimizer = optim.Adam(self.model.parameters(), lr=1e-4)
        objective = torch.nn.MSELoss()
        train_losses = []
        validation_losses = []
        num_epochs = 4
        loop = tqdm(total=len(self.train_dataset) + num_epochs, position=0)
        for epoch in range(num_epochs):
            train_dataset_use_entire = torch.clone(self.train_dataset)
            train_dataset_temp = torch.clone(self.train_dataset)

            val_dataset_use_entire = torch.clone(self.val_dataset)
            val_dataset_temp = torch.clone(self.val_dataset)
            for x in range(len(self.train_dataset)):
                if x % 3000 == 0 or x % 3000 == 1 or x % 3000 == 2:
                    pass
                else:
                    # move train_Data to its centroid, save centroid as a variable so that the objective loss will match the train targets better.
                    # s1 = time.time()
                    train_dataset_use = train_dataset_use_entire[x]  # this is the current row of the dataset
                    centroid = np.array([[0], [0], [0]])
                    for i in range(0, 4):
                        train_data_location = train_dataset_temp[x][i * 36 * 3:i * 36 * 3 + 36]
                        train_data_location = torch.reshape(train_data_location, (3, 12)).T
                        centroid = findCOM(train_data_location)
                        for j in range(len(train_data_location)):
                            train_dataset_use[i * 36 * 3 + j] = train_data_location[j, 0] - centroid[0, 0]

                            train_dataset_use[i * 36 * 3 + j + 12] = train_data_location[j, 1] - centroid[1, 0]

                            train_dataset_use[i * 36 * 3 + j + 24] = train_data_location[j, 2] - centroid[2, 0]
                        # centroid2 = findCOM(train_data_location)  #used to test if the centroid had changed.

                    # use the model moved to the centroid for predictions.
                    # s2 = time.time()
                    y_hat = self.model(train_dataset_use)
                    # s3 = time.time()

                    # next add the centroid back onto the y_hat so that the model can be prepared one to one to the train targets
                    # The centroid ends up being moved since the model rotates, so add in the
                    train_data_location = y_hat[0:36]
                    train_data_location = torch.reshape(train_data_location, (3, 12)).T
                    # newCentroid = findCOM(train_data_location)  - since the COM changed, adding in the original COM will translate it to where it originially was, plus the model's movement.
                    centroidMove = centroid
                    for j in range(len(train_data_location)):
                        train_data_location[j, 0] = train_data_location[j, 0] + centroidMove[0, 0]
                        train_data_location[j, 1] = train_data_location[j, 1] + centroidMove[1, 0]
                        train_data_location[j, 2] = train_data_location[j, 2] + centroidMove[2, 0]

                    # s4 = time.time()
                    optimizer.zero_grad()
                    loss = objective(y_hat, self.train_targets[x])

                    if x % 11000 == 3:
                        train_losses.append(loss.item())
                        validation_loss_list = []
                        for val_x in range(len(self.val_dataset)):
                            centroid = np.array([[0], [0], [0]])
                            val_dataset_use = val_dataset_use_entire[val_x]  # this is the current row of the dataset
                            for i in range(0, 4):
                                val_data_location = val_dataset_temp[val_x][i * 36 * 3:i * 36 * 3 + 36]
                                val_data_location = torch.reshape(val_data_location, (3, 12)).T
                                centroid = findCOM(val_data_location)
                                for j in range(len(val_data_location)):
                                    val_dataset_use[i * 36 * 3 + j] = val_data_location[j, 0] - centroid[0, 0]

                                    val_dataset_use[i * 36 * 3 + j + 12] = val_data_location[j, 1] - centroid[1, 0]

                                    val_dataset_use[i * 36 * 3 + j + 24] = val_data_location[j, 2] - centroid[2, 0]

                            val_y_hat = self.model(val_dataset_use)

                            val_data_location = val_y_hat[0:36]
                            val_data_location = torch.reshape(val_data_location, (3, 12)).T
                            # newCentroid = findCOM(train_data_location)  - since the COM changed, adding in the original COM will translate it to where it originially was, plus the model's movement.
                            centroidMove = centroid
                            for j in range(len(val_data_location)):
                                val_data_location[j, 0] = val_data_location[j, 0] + centroidMove[0, 0]
                                val_data_location[j, 1] = val_data_location[j, 1] + centroidMove[1, 0]
                                val_data_location[j, 2] = val_data_location[j, 2] + centroidMove[2, 0]

                            validation_loss_list.append(objective(val_y_hat, self.val_targets[val_x]))
                        validation_losses.append((sum(validation_loss_list) / float(len(validation_loss_list))).item())

                    loss.backward()
                    optimizer.step()
                    loop.set_description('epoch:{} loss:{:.4f} val_loss:{:.4f}'.format(epoch, loss.item(), validation_losses[-1]))
                    # s5= time.time()
                    if x % 2000 == 100:
                        print(x)
                        # print(s2 - s1)
                        # print(s3 - s2)
                        # print(s4 - s1)
                        # print(s5 - s4)
        torch.save(self.model.state_dict(), 'theModel.tar')
        loop.close()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(range(len(validation_losses)), validation_losses, label="Validation Loss")
        ax.plot(range(len(train_losses)), train_losses, label="Training loss")
        plt.legend()
        plt.show()


    def test(self):
        model = MLLinearNetwork.LinearNetwork(self.test_dataset).cuda()
        model.load_state_dict(torch.load('theModel.tar'))
        model = model.cuda()
        self.model = model
        objective = torch.nn.MSELoss()
        test_loss_list = []
        test_losses = []
        test_dataset_use_entire = torch.clone(self.test_dataset)
        test_dataset_temp = torch.clone(self.test_dataset)

        # the code below tests how well it guesses based off the correct initial data at each time step.
        for val_x in range(len(self.test_dataset)):
            centroid = np.array([[0], [0], [0]])
            test_dataset_use = test_dataset_use_entire[val_x]  # this is the current row of the dataset
            for i in range(0, 4):
                test_data_location = test_dataset_temp[val_x][i * 36 * 3:i * 36 * 3 + 36]
                test_data_location = torch.reshape(test_data_location, (3, 12)).T
                centroid = findCOM(test_data_location)
                for j in range(len(test_data_location)):
                    test_dataset_use[i * 36 * 3 + j] = test_data_location[j, 0] - centroid[0, 0]

                    test_dataset_use[i * 36 * 3 + j + 12] = test_data_location[j, 1] - centroid[1, 0]

                    test_dataset_use[i * 36 * 3 + j + 24] = test_data_location[j, 2] - centroid[2, 0]

            test_y_hat = self.model(test_dataset_use)

            test_data_location = test_y_hat[0:36]
            test_data_location = torch.reshape(test_data_location, (3, 12)).T
            # newCentroid = findCOM(train_data_location)  - since the COM changed, adding in the original COM will translate it to where it originially was, plus the model's movement.
            centroidMove = centroid
            for j in range(len(test_data_location)):
                test_data_location[j, 0] = test_data_location[j, 0] + centroidMove[0, 0]
                test_data_location[j, 1] = test_data_location[j, 1] + centroidMove[1, 0]
                test_data_location[j, 2] = test_data_location[j, 2] + centroidMove[2, 0]

            test_loss_list.append(objective(test_y_hat, self.test_targets[val_x]))
        test_losses.append((sum(test_loss_list) / float(len(test_loss_list))).item())
        print(test_losses)

        # now the test function will do the same test, but will use the output from the previous step as part of the next input.
        # starts with the correct 4 initial needed nodes, but then alters it each time with its guesses.
        test_loss_list = []
        test_losses = []
        test_dataset_use_entire = torch.clone(self.test_dataset)
        test_dataset_temp = torch.clone(self.test_dataset)

        # the code below tests how well it guesses based off the correct initial data at each time step.
        for val_x in range(len(self.test_dataset)):
            centroid = np.array([[0], [0], [0]])
            test_dataset_use = test_dataset_use_entire[val_x]  # this is the current row of the dataset
            for i in range(0, 4):
                test_data_location = test_dataset_temp[val_x][i * 36 * 3:i * 36 * 3 + 36]
                test_data_location = torch.reshape(test_data_location, (3, 12)).T
                centroid = findCOM(test_data_location)
                for j in range(len(test_data_location)):
                    test_dataset_use[i * 36 * 3 + j] = test_data_location[j, 0] - centroid[0, 0]

                    test_dataset_use[i * 36 * 3 + j + 12] = test_data_location[j, 1] - centroid[1, 0]

                    test_dataset_use[i * 36 * 3 + j + 24] = test_data_location[j, 2] - centroid[2, 0]

            test_y_hat = self.model(test_dataset_use)
            test_y_hat_clone = torch.clone(test_y_hat)
            test_y_hat_clone = test_y_hat_clone.cpu()
            test_y_hat_clone = test_y_hat_clone.detach().numpy()
            if np.size(self.nodeHist) == 0:
                self.nodeHist = np.array([test_y_hat_clone[0:36]])
            else:
                self.nodeHist = np.append(self.nodeHist, np.array([test_y_hat_clone[0:36]]), axis=0)  # this should add in the new output from the model using its own data for movement, needs to be
            # turned into nodes in the animate function.

            # only alteration compared to the first test block.- starts to change the relevant code snippets.
            if val_x < len(test_dataset_use) - 1:
                test_dataset_temp[val_x + 1][3 * 36 * 3:3 * 36 * 3 + 72] = test_y_hat
            if val_x < len(test_dataset_use) - 2:
                test_dataset_temp[val_x + 2][2 * 36 * 3:2 * 36 * 3 + 72] = test_y_hat
            if val_x < len(test_dataset_use) - 3:
                test_dataset_temp[val_x + 3][1 * 36 * 3:1 * 36 * 3 + 72] = test_y_hat
            if val_x < len(test_dataset_use) - 4:
                test_dataset_temp[val_x + 4][0 * 36 * 3:0 * 36 * 3 + 72] = test_y_hat

            test_data_location = test_y_hat[0:36]
            test_data_location = torch.reshape(test_data_location, (3, 12)).T
            # newCentroid = findCOM(train_data_location)  - since the COM changed, adding in the original COM will translate it to where it originially was, plus the model's movement.
            centroidMove = centroid
            for j in range(len(test_data_location)):
                test_data_location[j, 0] = test_data_location[j, 0] + centroidMove[0, 0]
                test_data_location[j, 1] = test_data_location[j, 1] + centroidMove[1, 0]
                test_data_location[j, 2] = test_data_location[j, 2] + centroidMove[2, 0]

            test_loss_list.append(objective(test_y_hat, self.test_targets[val_x]))
        test_losses.append((sum(test_loss_list) / float(len(test_loss_list))).item())
        print(test_losses)
        self.animateMotion(videoName='testML.avi')


    def animateMotion(self, videoName="default.avi"):
        """animates the motion of the system by graphing the system at various points in time and stitching those graphs
        together into a video.
        INPUT:
            videoName: the name to save the video file to.
        OUTPUT:
            None."""
        # parameters needed to set up graph and points to plot.
        x = []
        y = []
        z = []
        path = '/'
        time = np.arange(0, self.tf, self.dt)
        # This code determines what coordinates are connected by the strings.
        for t in time:
            t = int(t / self.dt)
            if t % int(1 / self.dt / 20) == 0:
                fig = plt.figure()
                ax = fig.add_subplot(projection='3d')
                # gets the coordinate points out of the given nodes.
                newNodeArray = []
                # print(self.nodeHist)
                for i in range(int(len(self.nodeHist[t].T) / 3)):
                    theNode = N.Node(self.nodeHist[t, i], self.nodeHist[t, i + 12], self.nodeHist[t, i + 24])

                    newNodeArray.append(theNode)

                # This code plots a scatterplot of the nodes, or in other words, shows the nodes on the graph without lines.
                ax.scatter3D(x, z, y, c=y, cmap='cividis')
                ax.set_xlim(-self.axisLength, self.axisLength)
                ax.set_ylim(-self.axisLength, self.axisLength)
                ax.set_zlim(-self.axisLength, self.axisLength)
                ax.set_xlabel('x')
                ax.set_ylabel('z')
                ax.set_zlabel('y')

                for i in range(0, len(newNodeArray)):
                    nodeCoords = newNodeArray[i].getCoords()
                    x.append(nodeCoords[0])
                    z.append(nodeCoords[1])
                    y.append(nodeCoords[2])
                    plt.plot(nodeCoords[0], nodeCoords[2], nodeCoords[1], '-go')
                    ax.text(nodeCoords[0], nodeCoords[2], nodeCoords[1], str(i + 1))

                for i in range(0, np.size(self.system.stringConn, 0)):
                    x = []
                    y = []
                    z = []
                    initialCoords = newNodeArray[self.system.stringConn[i, 0] - 1].getCoords()
                    finalCoords = newNodeArray[self.system.stringConn[i, 1] - 1].getCoords()
                    x.append(initialCoords[0])
                    x.append(finalCoords[0])
                    y.append(initialCoords[1])
                    y.append(finalCoords[1])
                    z.append(initialCoords[2])
                    z.append(finalCoords[2])
                    plt.plot(x, z, y, 'red')

                # This code determines what coordinates are connected by the bars.
                for i in range(0, np.size(self.system.barConn, 0)):
                    x = []
                    y = []
                    z = []
                    initialCoords = newNodeArray[self.system.barConn[i, 0] - 1].getCoords()
                    finalCoords = newNodeArray[self.system.barConn[i, 1] - 1].getCoords()
                    x.append(initialCoords[0])
                    x.append(finalCoords[0])
                    y.append(initialCoords[1])
                    y.append(finalCoords[1])
                    z.append(initialCoords[2])
                    z.append(finalCoords[2])
                    plt.plot(x, z, y, 'blue', linewidth=3)
                tString = str(t)
                tLength = len(str(int(time[-1] / self.dt)))
                if (len(tString) < tLength):
                    strFront = ''
                    for j in range(len(tString), tLength):
                        strFront = strFront + '0'
                    tString = strFront + tString
                plt.savefig(os.path.join(path, '../../placeholderFolders/pngFolder', ('myplot' + tString + ".png")), dpi=75)
                plt.close()
        print("some sort of animation error with the images for some reason, will need to look into it more")
        image_folder = os.path.join(path, '../../placeholderFolders/pngFolder')

        images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
        frame = cv2.imread(os.path.join(image_folder, images[0]))
        height, width, layers = frame.shape

        video = cv2.VideoWriter('videoFolder\\ML.mp4', 0, 20, (width, height))

        for image in images:
            video.write(cv2.imread(os.path.join(image_folder, image)))

        cv2.destroyAllWindows()
        video.release()
        folder_path = (r'C:\Users\blaye\Documents\School\Research\TensegrityDefinition\pngFolder')
        # using listdir() method to list the files of the folder
        test = os.listdir(folder_path)
        # taking a loop to remove all the images
        # using ".png" extension to remove only png images
        # using os.remove() method to remove the files
        for images in test:
            if images.endswith(".png"):
                os.remove(os.path.join(folder_path, images))


def findCOM(nodeVector):
    x = 0
    y = 0
    z = 0
    for i in range(len(nodeVector)):
        x = x + nodeVector[i, 0]
        y = y + nodeVector[i, 1]
        z = z + nodeVector[i, 2]
    x = x / len(nodeVector)
    y = y / len(nodeVector)
    z = z / len(nodeVector)
    return torch.tensor([[x], [y], [z]]).cuda()

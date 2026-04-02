"""This function will take the data from the states folder and transform it into a format that the MLTraining function
can use.  It will read in the information from csv's using pandas, stitch that data into new arrays meant for training,
and pass it into the training area."""
"""tips from Taylor:
  1. inputs several previous states (like 4) instead of just the previous state.  Will help the program have stability and the learning rate.
  2. outputs several next states - again helps with model stability so that it can learn to see into the future better
  3. learn the deltas, not the positions.  Makes the model more robust over wide input range.
  4. maybe use an RNN, previous information could help in the algorithm for some reason, but start vanilla."""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import matplotlib.pyplot as plt
from torchvision import transforms, utils, datasets
from tqdm import tqdm
from torch.nn.parameter import Parameter
import pdb
import pandas as pd

class DataImport():
    def __init__(self):
        self.info = []

    def importData(self,file = 'all'):
        """This function serves to import data from the files stored in the states folder.  It has the option to only import
           states from one file, or from all of the files.  For testing, will only be importing from 1 file at a time."""
        df = pd.read_csv('~\Documents\School\Research\TensegrityDefinition\csvsForLearning\\randomTarget.csv', header=0, index_col=0)
        #print(df)#gets entire df
        #print(df['0'])#gets column values
        #print(df.iloc[0]) # gets row values
        dataNumpy = df.to_numpy()
        #print(dataNumpy[0])  #row vector
        dataNumpyEnhanced = np.zeros((np.size(dataNumpy) - len(dataNumpy[0])) * 4)  #to be changed later
        dataNumpyEnhanced = dataNumpyEnhanced.reshape([len(dataNumpy) - 1, len(dataNumpy[0]) * 4])
        #print(len(dataNumpy[0]))
        #print(len(dataNumpyEnhanced[0]))
        for i in range(len(dataNumpy) - 1):
            #four vectors, all made out of data from numpy, with furthest back in time at front and most recent at end.
            if i < 3:
                vectorFirst = np.zeros(len(dataNumpy[0]))
            else:
                vectorFirst = dataNumpy[i - 3]

            if i < 2:
                vectorSecond = np.zeros(len(dataNumpy[0]))
            else:
                vectorSecond = dataNumpy[i - 2]

            if i < 1:
                vectorThird = np.zeros(len(dataNumpy[0]))
            else:
                vectorThird = dataNumpy[i - 1]

            vectorFourth = dataNumpy[i]
            appendedArray = np.append(vectorFirst, vectorSecond)
            appendedArray = np.append(appendedArray,vectorThird)
            appendedArray = np.array([np.append(appendedArray, vectorFourth)])


            dataNumpyEnhanced[i] = appendedArray


        dataTorchEnhanced = torch.tensor(dataNumpyEnhanced)
        dataTorchEnhanced = dataTorchEnhanced.cuda()  #This is meant to be the data to be imported as the training data;

        targetTorch = torch.tensor(dataNumpy[1:len(dataNumpy)]).cuda()# this is the targets that the ML algorithm should try to get to.
        return dataTorchEnhanced, targetTorch

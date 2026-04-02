"""The linear network class is to be used to create the architecture for the model. This will control what kind
    of techniques are used in creating the model, - like CNN, RNN, Transformer - and the overall structure of the
    network."""
"""tips from Taylor:
  1. inputs several previous states (like 4) instead of just the previous state.  Will help the program have stability and the learning rate.
  2. outputs several next states - again helps with model stability so that it can learn to see into the future better
  3. learn the deltas, not the positions.  Makes the model more robust over wide input range.
  4. maybe use an RNN, previous information could help in the algorithm for some reason, but start vanilla."""

  #This block will be to create the dataset.  Will probably need help creating this.

import torch
import torch.nn as nn


class LinearNetwork(nn.Module):
  def __init__(self,dataset):
    super(LinearNetwork, self).__init__()
    x = dataset
    h, w = x.size()
    output = 36*2 #this is the size of the output array of the next state delta.

    self.net = nn.Sequential(
        nn.Linear(w, 1000),
        nn.ReLU(),
        nn.Linear(1000,2000),
        nn.ReLU(),
        nn.Linear(2000,3000),
        nn.ReLU(),
        nn.Linear(3000,3000),
        nn.ReLU(),
        nn.Linear(3000,2000),
        nn.ReLU(),
        nn.Linear(2000,1000),
        nn.ReLU(),
        nn.Linear(1000,500),
        nn.ReLU(),
        nn.Linear(500,output)
    )
  def forward(self, x):
    return self.net(x)
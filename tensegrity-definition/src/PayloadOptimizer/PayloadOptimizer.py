# from gradient_free_optimizers import ParticleSwarmOptimizer
import numpy as np
from scipy.optimize import minimize
from typing import List

from src.PayloadOptimizer.SimplifiedTensegrityModel import SimplifiedTensegrityModel
from src.PayloadOptimizer.GA import geneticAlg


class PayloadOptimizer:
    """
    This class will preform the optimization on the simplified tensegrity model to include the payload model.  This optimization will conclude the following:
        1. the minimal equivilant spring constant for the tensegrity system depending on the shock type(meaning 1 side or either side). (springs are considered indestructible)
        2. optimal payload location given the payloads dimensions/ mass, again given as a function of shock type
        3. the minimal mass required for the connecting strings to hold the payload given a maximum stress constraint (the strings holding the mass will be assumed to be stiff)
            If needed the optimizer can choose material type based on the stresses on the material.  Could be altered to minimize cost if there is a maximum allowed cross sectional area for the
            strings.
        4.(optional)  time permitting, will create the minimal sized structure to keep the minimal equivilant spring constant within impact limits for the equipment in the middle.

        Constraints for the following system will as follows:
            1. No point on the payload may pass beyond the impacted nodes of the tensegrity model.
            2. stress in the strings holding the payload is not to go beyond their yield limit.
            3. The COM of the object must be placed at a point within the area of the base, if the base is approximated as a square.

    Ideally in the future the information that this presents will be capable of tuning/ sizing a tensegrity system - meaning that the size of the bars could be determined, and the minimal equivilant
    spring constant will be used to change the tension in the tensegrity strings, and the other information would make tensegrity design for these system much simpler.
    """

    def __init__(self, tensegrityModel: SimplifiedTensegrityModel = None):
        self.tensModel: SimplifiedTensegrityModel

        if tensegrityModel is None:

            # NOTE: The mass is also scaled when the system undergoes scaling, so if you have a predetermined scaling in mind, ensure that you compensate for
            #   the mass.
            self.tensModel = SimplifiedTensegrityModel(1, 10e1 * 3, timeFinal=1)
            initialPosition: np.ndarray[np.ndarray[float]] = self.tensModel.getInitialState()
            initialVelocity: np.ndarray[np.ndarray[float]] = np.zeros([7, 3])
            self.initialState: np.ndarray[np.ndarray[float]] = np.append(initialPosition, initialVelocity, axis=0)

            self.initialState.T[2][7:10] = np.ones(3) * 31.3
            self.tensModel.setInitialFullState(self.initialState)
        else:
            self.tensModel = tensegrityModel



    def optimize(self) ->  np.ndarray[np.ndarray[float]]:
        """
        The function that sets up and calls the optimizer for the state variables.
        :return:
        """
        # Notes so I can explain this to Harrison:
        # 1. tested points represent the final value that the geneticAlg returns
        # 2. The genetic algorithm is where the vast majority of computation occurs.
        # 3. The way that the genetic algorithm knows what model is being used (i.e. the Simplified model)
        #    is by passing in the objective function. That function calls a Value function, which value is
        #    determined by running the simplified dynamics.
        # 4. After the genetic algorithm is run, the tested points returns the final number of tested points,
        #    So everything after this function does not need to be changed.
        # 5. In order to change what parameters are used, the following need to be changed: a. The function
        #    to have a function size of only 1, with the corresponding range, b. The GAValue function so that it only
        #    assumes one argument, and c. The constraintDistanceReturn function, so it only uses one arg value.
        # NOTE: We confirmed tht the equivalent spring constant is linear for the model being squished, but we
        #       never tested how that corresponds to the spring constant of the top and bottom strings, probs needs validation.
        # Also Note: We need to add into the paper how we validated the linear spring constant, with a chart of the results.

        gs: List[float] = []
        testedPoints: np.ndarray[np.ndarray[float]] = geneticAlg(self.tensModel.GAValue, popSize=50, functionSize=4,
                                                                 maxGens=20, ranges=[[1000, 100], [1e-7,  1e-9], [3, .1], [.5, .5]])
        print(testedPoints)

        for i in range(len(testedPoints)):
            res, g = self.tensModel.constraintDistanceReturn(testedPoints[i], returnMore=True)

            print(res)
            gs.append(g)

        print()
        for i in range(len(gs)):
            print(gs[i])

        print()
        print(res)
        return res
        # self.tensModel.animateMotion("lowerAc.mp4")

        # search_space = {
        # "x1": np.arange(1000, 10000, .05),
        # }
        # opt = ParticleSwarmOptimizer(search_space, population=10)
        # opt.search(self.tensModel.GAParticleValue, n_iter=100)
        # print(opt)

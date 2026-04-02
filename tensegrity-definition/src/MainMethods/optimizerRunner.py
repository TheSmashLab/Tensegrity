import numpy as np

from src.PayloadOptimizer.SimplifiedTensegrityModel import SimplifiedTensegrityModel
from src.PayloadOptimizer.PayloadOptimizer import PayloadOptimizer

if __name__ == "__main__":
    """
    just a main method to run the optimizer that has been created.
    """
    tensModel = SimplifiedTensegrityModel(nodeMass=1, springConstant=10e1 * 3, timeFinal=1, payloadmass=.1)
    # tensModel.plotFigure()
    initialPosition = tensModel.getInitialState()
    initialVelocity = np.zeros([7, 3])
    initialState = np.append(initialPosition, initialVelocity, axis=0) 
    #
    # # tensModel.rk4(initialState)
    # # tensModel.animateMotion("simplifiedTest.mp4")
    # 1.164e+00 2.371e-08 4.678e-01 4.959e+00 4.690e+02
    initialState.T[2][10:13] = np.ones(3) * 31.3
    tensModel.setInitialFullState(initialState)

    # tensModel.setEquSpringConst(1.693e+01)
    # tensModel.setStiffSpringConstant(5.523e-07)
    # tensModel.setStructureSize( 2.095e+01)
    # tensModel.setPayloadLocation(1)
    # tensModel.rk4(initialState)
    # tensModel.animateMotion("GAattempt.mp4")
    #
    # initialState.T[2][10:13] = np.ones(3) * 40
    # tensModel.setInitialFullState(initialState)
    #
    # tensModel.setEquSpringConst(10e1 * 3)
    # print(tensModel.constraintDistanceReturn(0))
    # tensModel.animateMotion("eqOf300.mp4")
    #
    # print()
    #

    # tensModel.animateMotion("Eq1000.mp4")

    optimzer = PayloadOptimizer(tensegrityModel=tensModel)
    optimzer.optimize()

    # randomSpeeds = 20
    # initialVelocity = np.random.rand(7, 3) * randomSpeeds - np.ones([7, 3]) * randomSpeeds/2
    # initialState = np.append(initialPosition, initialVelocity, axis = 0)
    # initialState.T[2][7:13] = np.ones(6) * 10
    # tensModel.rk4(initialState)
    # tensModel.animateMotion("randomInitVel.mp4")

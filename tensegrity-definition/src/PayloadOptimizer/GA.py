import numpy
import numpy as np
import matplotlib.pyplot as plt
from typing import List


def binaryCrossover(parents, values):
    children = np.zeros([len(values), len(values[0]) - 1])
    for i in range(len(parents[0])):
        betterParent = int(parents[0][i])
        otherParent = int(parents[1][i])
        if parents[1][i] < parents[0][i]:
            betterParent = int(parents[1][i])
            otherParent = int(parents[0][i])
        child1 = np.zeros((1, len(values[0]) -1))
        child2 = np.zeros((1, len(values[0]) -1))
        for j in range(len(child1[0])):
            if np.random.random() < .5:
                child1[0][j] = values[betterParent][j]
                child2[0][j] = values[otherParent][j]
            else:
                child1[0][j] = values[otherParent][j]
                child2[0][j] = values[betterParent][j]
        children[2 * i] = child1
        children[2 * i + 1] = child2
    return children


def geneticAlg(function, popSize: int, functionSize: int, ranges: List[List], maxGens: int = 20, mutationFactor: float = .05):
    """
    The typical genetic algorithm.  It essentially takes any objective function, with as many variables as needed, and minimizes the results.
    Parameters
    ----------
    function:  the objective function that is to be minimized.
    popSize:  The size of the population to be tested, the higher the number, typically the better result of the simulation.
    functionSize:  The number of parameters the function takes.
    ranges: The range that the initial function parameters should be initilaized between.  Takes a range and an offset as a 2D list.
    maxGens:  the number of iterations the function should work through.
    mutationFactor: the amount a variable should mutate if randomly selected.

    Returns
    -------
    allTestedPoints:  A list of points tested for their fitness, organized from best to worst.
    """
    initialPoints: np.ndarray[np.ndarray[float]] = np.zeros([popSize, functionSize])

    for i in range(len(ranges)):
        initialPointsToAdd: np.ndarray[np.ndarray[float]] = np.random.random(popSize) * ranges[i][0] + np.ones([popSize]) * ranges[i][1]
        initialPoints.T[i] = initialPointsToAdd

    values: np.ndarray[np.ndarray[float]] = np.zeros([popSize, functionSize + 1])

    for i in range(popSize):
        values[i][:functionSize] = initialPoints[i]
        values[i][functionSize] = function(initialPoints[i])

    values = values[values[:, len(values[0]) - 1].argsort()]
    allTestedPoints: List[float] = []
    numpy.set_printoptions(precision=3, linewidth=100)

    for k in range(maxGens):
        print(values)

        # Tournament select - selects only parents to be used in breeding children
        parentPairs = tournamentSelect(values)

        # Create children
        children = linearCrossover(parentPairs, values)
        moreChildren = binaryCrossover(parentPairs, values)
        children = mutate(children, mutationFactor, ranges)
        moreChildren = mutate(moreChildren, mutationFactor, ranges)

        # Pops the values2 with children info
        values2 = np.zeros([popSize * 2, functionSize + 1])

        for i in range(popSize):
            values2[i * 2][:functionSize] = children[i]
            values2[i * 2][functionSize] = function(children[i])
            values2[i * 2 + 1][:functionSize] = moreChildren[i]
            values2[i * 2 + 1][functionSize] = function(moreChildren[i])

        valsComb = np.append(values, values2, axis=0)
        valsComb = valsComb[valsComb[:, len(valsComb[0]) - 1].argsort()]
        valsComb = replaceInfValues(valsComb, ranges, function)
        valsComb = valsComb[valsComb[:, len(valsComb[0]) - 1].argsort()]

        # Reselects somewhat randomly the combination of the parents and children points, based off fitness.
        # So best and worst of the rendition guaranteed to be kept.
        newTotNodes = tournamentSelectParAndChild(valsComb)

        # Resets values for the iteration.
        for i in range(popSize):
            values[i] = valsComb[int(newTotNodes[i])]

        values = values[values[:, len(values[0]) - 1].argsort()]

        if k == maxGens - 1:
            allTestedPoints = values[values[:, len(values[0]) - 1].argsort()]

        print()
        print()
    return allTestedPoints


def linearCrossover(parents: np.ndarray[np.ndarray[float]], values: np.ndarray[np.ndarray[float]]) -> np.ndarray[np.ndarray[float]]:
    """
    Generates the children from the parents, assigns the children to the next generation.
    :param parents: the parents of the children values, what nodes will be combined to make the next generation
    :param values: the fitness of each point, with their state variables and the fitness value.
    :return: the children created from the cross-over.
    """
    # Crosses the parent pairs, creates the new children, returns the children
    children: np.ndarray[np.ndarray[float]] = np.zeros([len(values), len(values[0]) - 1])

    for i in range(len(parents[0])):
        betterParent: int = int(parents[0][i])
        otherParent: int = int(parents[1][i])

        if parents[1][i] < parents[0][i]:
            betterParent: int = int(parents[1][i])
            otherParent: int = int(parents[0][i])

        child1: np.ndarray[float] = values[betterParent][:len(values[0]) - 1] * .5 + values[otherParent][:len(values[0]) - 1] * .5
        child2: np.ndarray[float] = values[betterParent][:len(values[0]) - 1] * 2 - values[otherParent][:len(values[0]) - 1]
        children[2 * i] = child1
        children[2 * i + 1] = child2

    return children


def mutate(childrenVals: np.ndarray[float], deltaMax: float, ranges: np.ndarray[float], mutationRate: float=.05):
    """
    :param childrenVals: the values of the children
    :param deltaMax: maximum allows to mutate by
    :param ranges: The ranges of the values (for scaling).
    :param mutationRate: how often mutation will occur.
    :return: The mutated children values.
    """
    for i in range(len(childrenVals)):
        for j in range(len(childrenVals[0])):
            if np.random.random(1) < mutationRate:
                childrenVals[i][j] = childrenVals[i][j] + (np.random.random(1) - .5) * deltaMax * ranges[j][1]

    return childrenVals


def replaceInfValues(values: np.ndarray[float], ranges: np.ndarray[float], function) -> np.ndarray[float]:
    """
    Replaces inf child values so that more feasible children are created initially
    :param values: the child values.
    :param ranges: The ranges the child values can be between.
    :param function: The objective function
    :return: The new values.
    """
    for i in range(len(values) - 1, 0, -1):
        if values[i][len(values[0]) - 1] != np.inf:
            break

        childtmp: np.ndarray[float] = np.array([values[0][:len(values[0]) - 1]])
        childtmp = mutate(childtmp, .1, ranges, mutationRate=1)
        values[i][:len(values[0]) - 1] = childtmp
        values[i][len(values[0]) - 1] = function(values[i])

    return values


def tournamentSelect(values: np.ndarray[np.ndarray[float]]) -> np.ndarray[float]:
    """
    A tournament selection for parents of the algorithm's future children.
    :param values: The values array of how each point preformed.
    :return: the random parent ordering for linear crossover.
    """
    # this function will do tournaments between random pairs in the population, with each point being selected exactly 2x.
    number: np.ndarray[float] = np.arange(len(values))
    randomOrder1: np.ndarray[float] = np.random.choice(number, len(values), False)
    firstParents: np.ndarray[float] = np.zeros(int(len(values) / 2))
    randomOrder2: np.ndarray[float] = np.random.choice(number, len(values), False)
    secondParents: np.ndarray[float] = np.zeros(int(len(values) / 2))

    for i in range(len(firstParents)):
        theNode1: np.ndarray[float] = randomOrder1[i * 2]

        if randomOrder1[i * 2 + 1] < theNode1:
            theNode1 = randomOrder1[i * 2 + 1]

        firstParents[i] = int(theNode1)

        theNode2: np.ndarray[float] = randomOrder2[i * 2]

        if randomOrder2[i * 2 + 1] < theNode2:
            theNode2 = randomOrder2[i * 2 + 1]

        secondParents[i] = int(theNode2)

    return np.array([firstParents, secondParents])


def tournamentSelectParAndChild(values: np.ndarray[float]) -> np.ndarray[int]:
    """
    A tournament selection for parents of the algorithm's future children.
    :param values: The values array of how each point preformed.
    :return:     the random parent ordering for linear crossover.
    """
    number: np.ndarray[float] = np.arange(len(values))
    randomOrder1: np.ndarray[float] = np.random.choice(number, len(values), False)
    firstParents: np.ndarray[int] = np.zeros(int(len(values) / 3))

    for i in range(len(firstParents)):
        theNode1: np.ndarray[float] = randomOrder1[i * 3]

        if randomOrder1[i * 3 + 1] < theNode1:
            theNode1 = randomOrder1[i * 3 + 1]

        if randomOrder1[i * 3 + 2] < theNode1:
            theNode1 = randomOrder1[i * 3 + 2]

        firstParents[i]: int = int(theNode1)

    return firstParents

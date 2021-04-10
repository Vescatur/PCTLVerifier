import math

from config import RELATIVE_ERROR_TARGET, UPPER_BOUND_HEURISTIC, PRINT_OVI_ERROR_BOUNDS
from value_pctl_solver import findStatesWithCorrectProbability, createInitialProbabilityToReachGoal, \
    findProbabilityToReachGoal, stepForSingleState, calculateRelativeError


def findStatesWithOptimisticValueIteration(network, universe, allowedStates, goalStates, isEquals, isLessThan, isMax, probabilityTarget):
    initialProbabilityToReachGoal = createInitialProbabilityToReachGoal(universe, goalStates)

    probabilityToReachGoal = findProbabilityToReachGoalWithOptimisticValueIteration(network, universe, allowedStates, goalStates, isMax, initialProbabilityToReachGoal, RELATIVE_ERROR_TARGET)
    returnStates = findStatesWithCorrectProbability(goalStates,allowedStates,probabilityToReachGoal,probabilityTarget,isLessThan,isEquals)
    return returnStates


def findProbabilityToReachGoalWithOptimisticValueIteration(network, universe, allowedStates, goalStates, isMax, probabilityToReachGoal, relativeErrorTarget):
    lowerProbabilityToReachGoal = findProbabilityToReachGoal(network, allowedStates, goalStates, isMax, probabilityToReachGoal, relativeErrorTarget)
    upperProbabilityToReachGoal = createUpperProbabilityToReachGoal(universe, lowerProbabilityToReachGoal)
    for i in range(1, math.ceil(1/relativeErrorTarget)):
        up = True
        down = True
        error = 0
        for stateFrom in allowedStates:
            if stateFrom in goalStates:
                continue
            newLowerProbabilityToReachGoal = stepForSingleState(network,stateFrom,lowerProbabilityToReachGoal, isMax)
            newUpperProbabilityToReachGoal = stepForSingleState(network,stateFrom,upperProbabilityToReachGoal, isMax)
            if newLowerProbabilityToReachGoal > 0:
                error = max(error,calculateRelativeError(lowerProbabilityToReachGoal[stateFrom], newLowerProbabilityToReachGoal))
            if newUpperProbabilityToReachGoal < upperProbabilityToReachGoal[stateFrom]:
                up = False
                upperProbabilityToReachGoal[stateFrom] = newUpperProbabilityToReachGoal
            if newUpperProbabilityToReachGoal > upperProbabilityToReachGoal[stateFrom]:
                down = False
            lowerProbabilityToReachGoal[stateFrom] = newLowerProbabilityToReachGoal
            if lowerProbabilityToReachGoal[stateFrom] > upperProbabilityToReachGoal[stateFrom]:
                return findProbabilityToReachGoalWithOptimisticValueIteration(network, universe, allowedStates, goalStates, isMax, lowerProbabilityToReachGoal, relativeErrorTarget/2)
        if down:
            return createAverageProbabilityToReachGoal(universe, lowerProbabilityToReachGoal, upperProbabilityToReachGoal)
        if up:
            return findProbabilityToReachGoalWithOptimisticValueIteration(network, universe, allowedStates, goalStates, isMax, lowerProbabilityToReachGoal, relativeErrorTarget/2)
    return findProbabilityToReachGoalWithOptimisticValueIteration(network, universe, allowedStates, goalStates, isMax, lowerProbabilityToReachGoal, relativeErrorTarget/2)


def createUpperProbabilityToReachGoal(universe, lowerProbabilityToReachGoal):
    upperProbabilityToReachGoal = dict()
    for state in universe:
        upperProbabilityToReachGoal[state] = min(lowerProbabilityToReachGoal[state] * (1 + UPPER_BOUND_HEURISTIC), 1)
    return upperProbabilityToReachGoal


def createAverageProbabilityToReachGoal(universe, lowerProbability, upperProbability):
    probabilityToReachGoal = dict()

    if PRINT_OVI_ERROR_BOUNDS:
        print("Optimistic Value Iteration")
    for state in universe:
        if PRINT_OVI_ERROR_BOUNDS:
            print(str(state) + " error bound is [" + str(lowerProbability[state]) + "," + str(
                upperProbability[state]) + "]")

        probabilityToReachGoal[state] = (lowerProbability[state] + upperProbability[state]) / 2
    return probabilityToReachGoal
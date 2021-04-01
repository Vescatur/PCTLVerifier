from config import RELATIVE_ERROR_TARGET


def findStatesWithProbabilityUntil(network, universe, allowedStates, goalStates, isEquals, isLessThan, isMax,
                                   probabilityTarget):
    initialProbabilityToReachGoal = createInitialProbabilityToReachGoal(universe, goalStates)

    probabilityToReachGoal = findProbabilityToReachGoal(network, allowedStates, goalStates, isMax, initialProbabilityToReachGoal, RELATIVE_ERROR_TARGET)
    returnStates = findStatesWithCorrectProbability(goalStates,allowedStates,probabilityToReachGoal,probabilityTarget,isLessThan,isEquals)
    return returnStates


def createInitialProbabilityToReachGoal(universe, goalStates):
    initialProbabilityToReachGoal = dict()
    for state in universe:
        initialProbabilityToReachGoal[state] = 0
    for state in goalStates:
        initialProbabilityToReachGoal[state] = 1
    return initialProbabilityToReachGoal


def findProbabilityToReachGoal(network, allowedStates, goalStates, isMax, probabilityToReachGoal, relativeErrorTarget):
    maxRelativeError = 1
    while maxRelativeError >= relativeErrorTarget:
        maxRelativeError = 0
        for stateFrom in allowedStates:
            if stateFrom in goalStates:
                continue
            outerProbability = stepForSingleState(network,stateFrom,probabilityToReachGoal, isMax)
            if outerProbability != 0:
                maxRelativeError = max(maxRelativeError, calculateRelativeError(probabilityToReachGoal[stateFrom], outerProbability))
            probabilityToReachGoal[stateFrom] = outerProbability
    return probabilityToReachGoal


def calculateRelativeError(oldProbability, newProbability):
    return abs(newProbability - oldProbability) / newProbability

def stepForSingleState(network,stateFrom,probabilityReachGoal, isMax):
    outerProbability = -1
    transitions = network.get_transitions(stateFrom)
    for transition in transitions:
        branches = network.get_branches(stateFrom, transition)
        probability = 0
        for branch in branches:
            stateTo = network.jump(stateFrom, transition, branch)
            probability = probability + branch.probability * probabilityReachGoal[stateTo]
        if outerProbability == -1 or \
                (outerProbability <= probability and isMax) or \
                (outerProbability >= probability and not isMax):
            outerProbability = probability
    if outerProbability == -1:
        return probabilityReachGoal[stateFrom]
    return outerProbability


def findStatesWithCorrectProbability(goalStates,allowedStates,probabilityToReachGoal,probabilityTarget,isLessThan,isEquals):
    returnStates = goalStates.copy()
    for state in allowedStates:
        if (probabilityToReachGoal[state] <= probabilityTarget and isLessThan and isEquals) or \
                (probabilityToReachGoal[state] < probabilityTarget and isLessThan and not isEquals) or \
                (probabilityToReachGoal[state] >= probabilityTarget and not isLessThan and isEquals) or \
                (probabilityToReachGoal[state] > probabilityTarget and not isLessThan and not isEquals):
            returnStates.add(state)
    return returnStates


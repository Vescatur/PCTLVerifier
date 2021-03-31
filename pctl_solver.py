

def findStatesWithProbabilityUntil(network, universe, allowedStates, goalStates, isEquals, isLessThan, isMax,
                                   probabilityTarget):
    probabilityToReachGoal = findProbabilityToReachGoal(network, universe, allowedStates, goalStates, isMax)
    returnStates = goalStates.copy()
    for state in allowedStates:
        if (probabilityToReachGoal[state] <= probabilityTarget and isLessThan and isEquals) or \
                (probabilityToReachGoal[state] < probabilityTarget and isLessThan and not isEquals) or \
                (probabilityToReachGoal[state] >= probabilityTarget and not isLessThan and isEquals) or \
                (probabilityToReachGoal[state] > probabilityTarget and not isLessThan and not isEquals):
            returnStates.add(state)
    return returnStates


def findProbabilityToReachGoal(network, universe, allowedStates, goalStates, isMax):
    probabilityToReachGoal = dict()
    for state in universe:
        probabilityToReachGoal[state] = 0
    for state in goalStates:
        probabilityToReachGoal[state] = 1

    maxRelativeError = 1
    while maxRelativeError >= 0.1:
        maxRelativeError = 0
        for stateFrom in allowedStates:
            if stateFrom in goalStates:
                continue
            outerProbability = stepForSingleState(network,stateFrom,probabilityToReachGoal, isMax)
            if outerProbability != -1:
                if outerProbability != 0:
                    relativeError = abs(outerProbability - probabilityToReachGoal[stateFrom]) / outerProbability
                    if maxRelativeError < relativeError:
                        maxRelativeError = relativeError
                probabilityToReachGoal[stateFrom] = outerProbability
    return probabilityToReachGoal


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
    return outerProbability

def findStatesWithOptimisticValueIteration():
    print("a")

def findProbabilityToReachGoalWithOptimisticValueIteration():
    print("b")
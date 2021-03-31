

def findStatesWithUntilStepBounded(network, allowedStates, goalStates, maxSteps, returnStates, forAll):
    changed = True
    i = 1
    while changed and (maxSteps == -1 or i <= maxSteps):
        i = i + 1
        changed = False
        statesForSingleStep = set()
        for state in allowedStates:
            if state not in returnStates:
                nextStates = getAllNewStates(network, state)
                shouldAdd = forAll
                if len(nextStates) == 0:
                    shouldAdd = False
                else:
                    for nextState in nextStates:
                        if (nextState in returnStates or nextState in goalStates) and not forAll:
                            shouldAdd = True
                            break
                        elif (nextState not in returnStates and nextState not in goalStates) and forAll:
                            shouldAdd = False
                            break
                if shouldAdd:
                    changed = True
                    statesForSingleStep.add(state)
        if changed:
            returnStates = returnStates.union(statesForSingleStep)
    return returnStates


def findStatesWithUntil(network, allowedStates, goalStates, returnStates, forAll):
    changed = True
    i = 1
    while changed:
        i = i + 1
        changed = False
        for state in allowedStates:
            if state not in returnStates:
                nextStates = getAllNewStates(network, state)
                shouldAdd = forAll
                if len(nextStates) == 0:
                    shouldAdd = False
                else:
                    for nextState in nextStates:
                        if (nextState in returnStates or nextState in goalStates) and not forAll:
                            shouldAdd = True
                            break
                        elif (nextState not in returnStates and nextState not in goalStates) and forAll:
                            shouldAdd = False
                            break
                if shouldAdd:
                    changed = True
                    returnStates.add(state)
    return returnStates


def getAllNewStates(network, state):
    nextStates = set()
    transitions = network.get_transitions(state)
    for transition in transitions:
        branches = network.get_branches(state, transition)
        for branch in branches:
            nextState = network.jump(state, transition, branch)
            nextStates.add(nextState)
    return nextStates
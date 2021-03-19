import sys
from importlib import util
from timeit import default_timer as timer

if len(sys.argv) < 2:
    print("Error: No model specified.")
    quit()
print("Loading model from \"{0}\"...".format(sys.argv[1]), end="", flush=True)
spec = util.spec_from_file_location("model", sys.argv[1])
model = util.module_from_spec(spec)
spec.loader.exec_module(model)


def start():
    network = model.Network()
    universe = createUniverse(network)
    print("The model has " + str(len(universe)) + " reachable states.")
    initialState = network.get_initial_state()
    for i in range(len(network.properties)):
        start_time = timer()
        propertie = network.properties[i]
        result = checkSingleProperty(universe, network, propertie, initialState)
        end_time = timer()
        print("property " + str(propertie) + " is " + str(result) + ". The calculation took " + str(
            end_time - start_time) + " seconds.")


# finds the reachable universe of a model
def createUniverse(network):
    universe = set()
    toDoStates = set()
    initialState = network.get_initial_state()
    universe.add(initialState)
    toDoStates.add(initialState)
    while len(toDoStates) >= 1:
        state = toDoStates.pop()
        transitions = network.get_transitions(state)
        for transition in transitions:
            branches = network.get_branches(state, transition)
            for branch in branches:
                nextState = network.jump(state, transition, branch)
                if nextState not in universe:
                    universe.add(nextState)
                    toDoStates.add(nextState)
    return universe


def checkSingleProperty(universe, network, propertie, initialState):
    trueStates = checkSinglePropertyExpression(universe, network, propertie.exp)
    return initialState in trueStates


def checkSinglePropertyExpression(universe, network, propertyExpression):
    logicalExpressions = {"ap", "or", "not", "and"}
    selectorExpressions = {"exists", "forall"}
    pathExpressions = {"until", "next", "step-bounded-always", "step-bounded-eventually",
                       "step-bounded-until", "eventually", "always"}
    comparisonExpressions = {"<", ">", "<=", ">="}
    probabilityExpressions = {"p_min", "p_max"}

    op = propertyExpression.op
    if op in logicalExpressions:
        return checkLogicalExpression(universe, network, propertyExpression)
    elif op in selectorExpressions:
        return checkSelectorExpression(universe, network, propertyExpression)
    elif op in comparisonExpressions:
        return checkComparisonExpressions(universe, network, propertyExpression)
    elif op in probabilityExpressions:
        raise Exception("incorrectly formatted property")
    elif op in pathExpressions:
        raise Exception("incorrectly formatted property")
    else:
        print(op)
        raise Exception("unsupported propertyExpression")


def skip(universe, network, propertyExpression):
    return checkSinglePropertyExpression(universe, network, propertyExpression.args[0])


def checkLogicalExpression(universe, network, propertyExpression):
    if propertyExpression.op == "ap":
        states = set()
        for state in universe:
            if network.get_expression_value(state, propertyExpression.args[0]):
                states.add(state)
        return states
    elif propertyExpression.op == "not":
        states = checkSinglePropertyExpression(universe, network, propertyExpression.args[0])
        return universe - states
    elif propertyExpression.op == "or":
        states1 = checkSinglePropertyExpression(universe, network, propertyExpression.args[0])
        states2 = checkSinglePropertyExpression(universe, network, propertyExpression.args[1])
        return states1.union(states2)
    elif propertyExpression.op == "and":
        states1 = checkSinglePropertyExpression(universe, network, propertyExpression.args[0])
        states2 = checkSinglePropertyExpression(universe, network, propertyExpression.args[1])
        return states1.intersection(states2)
    else:
        raise Exception("unsupported propertyExpression")


def checkSelectorExpression(universe, network, selectorPropertyExpression):
    forAll = None
    if selectorPropertyExpression.op == "exists":
        forAll = False
    elif selectorPropertyExpression.op == "forall":
        forAll = True
    else:
        raise Exception("unsupported propertyExpression")

    propertyExpression = selectorPropertyExpression.args[0]
    if propertyExpression.op == "until":
        allowedStates = checkSinglePropertyExpression(universe, network, propertyExpression.args[0])
        goalStates = checkSinglePropertyExpression(universe, network, propertyExpression.args[1])
        return findStatesWithUntil(network, allowedStates, goalStates, -1, goalStates, forAll)
    elif propertyExpression.op == "eventually":
        goalStates = checkSinglePropertyExpression(universe, network, propertyExpression.args[0])
        return findStatesWithUntil(network, universe, goalStates, -1, goalStates, forAll)
    elif propertyExpression.op == "always":
        expression1 = model.PropertyExpression("not", [propertyExpression.args[0]])
        expression2 = model.PropertyExpression("eventually", [expression1])
        expression3 = None
        if forAll:
            expression3 = model.PropertyExpression("exists", [expression2])
        else:
            expression3 = model.PropertyExpression("forall", [expression2])

        expression4 = model.PropertyExpression("not", [expression3])
        return checkSinglePropertyExpression(universe, network, expression4)
    elif propertyExpression.op == "next":
        goalStates = checkSinglePropertyExpression(universe, network, propertyExpression.args[0])
        return findStatesWithUntil(network, universe, goalStates, 1, set(), forAll)
    elif propertyExpression.op == "step-bounded-until":
        allowedStates = checkSinglePropertyExpression(universe, network, propertyExpression.args[0])
        goalStates = checkSinglePropertyExpression(universe, network, propertyExpression.args[1])
        return findStatesWithUntil(network, allowedStates, goalStates, propertyExpression.args[2], goalStates, forAll)
    elif propertyExpression.op == "step-bounded-eventually":
        goalStates = checkSinglePropertyExpression(universe, network, propertyExpression.args[0])
        return findStatesWithUntil(network, universe, goalStates, propertyExpression.args[1], goalStates, forAll)
    elif propertyExpression.op == "step-bounded-always":
        expression1 = model.PropertyExpression("not", [propertyExpression.args[0]])
        expression2 = model.PropertyExpression("step-bounded-eventually", [expression1, propertyExpression.args[1]])
        expression3 = None
        if forAll:
            expression3 = model.PropertyExpression("exists", [expression2])
        else:
            expression3 = model.PropertyExpression("forall", [expression2])
        expression4 = model.PropertyExpression("not", [expression3])
        return checkSinglePropertyExpression(universe, network, expression4)
    else:
        raise Exception("unsupported propertyExpression")


def findStatesWithUntil(network, allowedStates, goalStates, maxSteps, returnStates, forAll):
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


def getAllNewStates(network, state):
    nextStates = set()
    transitions = network.get_transitions(state)
    for transition in transitions:
        branches = network.get_branches(state, transition)
        for branch in branches:
            nextState = network.jump(state, transition, branch)
            nextStates.add(nextState)
    return nextStates


def checkComparisonExpressions(universe, network, propertyExpression):
    probability = propertyExpression.args[1]
    if not isinstance(probability, float):
        raise Exception("incorrectly formatted property")

    isMax = None
    probabilityExpression = propertyExpression.args[0]
    if probabilityExpression.op == "p_min":
        isMax = False
    elif probabilityExpression.op == "p_max":
        isMax = True
    else:
        raise Exception("incorrectly formatted property")

    isEquals = None
    isLessThan = None
    if propertyExpression.op == "<":
        isEquals = False
        isLessThan = True
    elif propertyExpression.op == "<=":
        isEquals = True
        isLessThan = True
    elif propertyExpression.op == ">":
        isEquals = False
        isLessThan = False
    elif propertyExpression.op == ">=":
        isEquals = True
        isLessThan = False
    else:
        raise Exception("incorrectly formatted property")

    pathExpression = probabilityExpression.args[0]
    if pathExpression.op == "until":
        allowedStates = checkSinglePropertyExpression(universe, network, pathExpression.args[0])
        goalStates = checkSinglePropertyExpression(universe, network, pathExpression.args[1])
        return findStatesWithProbabilityUntil(network, universe, allowedStates, goalStates, isEquals, isLessThan, isMax,
                                              probability)
    elif pathExpression.op == "eventually":
        goalStates = checkSinglePropertyExpression(universe, network, pathExpression.args[0])
        return findStatesWithProbabilityUntil(network, universe, universe, goalStates, isEquals, isLessThan, isMax,
                                              probability)
    elif pathExpression.op == "always":
        expression1 = model.PropertyExpression("not", [pathExpression.args[0]])
        expression2 = model.PropertyExpression("eventually", [expression1])
        expression3 = None
        expression4 = None
        if isMax:
            expression3 = model.PropertyExpression("p_min", [expression2])
            if isEquals:
                expression4 = model.PropertyExpression(">", [expression3, 1 - probability]) # this doesn't work
            else:
                expression4 = model.PropertyExpression(">=", [expression3, 1 - probability])
        else:
            expression3 = model.PropertyExpression("p_max", [expression2])
            if isEquals:
                expression4 = model.PropertyExpression("<", [expression3, 1 - probability])
            else:
                expression4 = model.PropertyExpression("<=", [expression3, 1 - probability])

        return checkSinglePropertyExpression(universe, network, expression4)
    elif pathExpression.op == "next":
        raise Exception("unsupported propertyExpression")
    elif pathExpression.op == "step-bounded-always":
        raise Exception("unsupported propertyExpression")
    elif pathExpression.op == "step-bounded-eventually":
        raise Exception("unsupported propertyExpression")
    elif pathExpression.op == "step-bounded-until":
        raise Exception("unsupported propertyExpression")
    else:
        raise Exception("incorrectly formatted property")


def findStatesWithProbabilityUntil(network, universe, allowedStates, goalStates, isEquals, isLessThan, isMax,
                                   probabilityTarget):
    probabilityReachGoal = dict()
    for state in universe:
        probabilityReachGoal[state] = 0
    for state in goalStates:
        probabilityReachGoal[state] = 1

    maxRelativeError = 1
    while maxRelativeError >= 0.1:
        maxRelativeError = 0
        for stateFrom in allowedStates:
            if stateFrom in goalStates:
                continue
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
            if outerProbability != -1:
                if outerProbability != 0:
                    relativeError = abs(outerProbability - probabilityReachGoal[stateFrom]) / outerProbability
                    if maxRelativeError < relativeError:
                        maxRelativeError = relativeError
                probabilityReachGoal[stateFrom] = outerProbability

    returnStates = goalStates.copy()
    for state in allowedStates:
        if (probabilityReachGoal[state] <= probabilityTarget and isLessThan and isEquals) or \
                (probabilityReachGoal[state] < probabilityTarget and isLessThan and not isEquals) or \
                (probabilityReachGoal[state] >= probabilityTarget and not isLessThan and isEquals) or \
                (probabilityReachGoal[state] > probabilityTarget and not isLessThan and not isEquals):
            returnStates.add(state)
    return returnStates


start()

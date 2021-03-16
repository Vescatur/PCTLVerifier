# Run as python checker-demo.py model.py
# Requires Python 3.7 or newer

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
    network = model.Network()  # create network instance
    universe = createUniverse(network)
    print("The model has " + str(len(universe)) + " reachable states.")
    initialState = network.get_initial_state()
    for i in range(len(network.properties)):
        start_time = timer()
        property = network.properties[i]
        result = checkSingleProperty(universe, network, property, initialState)
        end_time = timer()
        print("property "+ str(property) + " is " + str(result)+ ". The calculation took "+str(end_time-start_time) + " seconds.")


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


def checkSingleProperty(universe, network, property, initialState):
    trueStates = checkSinglePropertyExpression(universe, network, property.exp)
    return initialState in trueStates


def checkSinglePropertyExpression(universe, network, propertyExpression):
    logicalExpressions = {"ap", "or", "not", "and"}
    selectorExpressions = {"exists", "forall"}
    pathExpressions = {"until", "next", "step-bounded-always", "step-bounded-eventually",
                       "step-bounded-until", "eventually", "always"}
    op = propertyExpression.op
    if op in logicalExpressions:
        return checkLogicalExpression(universe, network, propertyExpression)
    elif op in selectorExpressions:
        return checkSelectorExpression(universe, network, propertyExpression)
    elif op in pathExpressions:
        return checkPathExpression(universe, network, propertyExpression)
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

    # print(propertyExpression.op)
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

    # F<> eventually
    # Get set A which holds to the condition
    # Go through set A and add all predisesors to A. Add itself to B and remove itself from A.
    # G[] always
    # X next
    # U until


def checkPathExpression(universe, network, propertyExpression):
    raise Exception("incorrectly formatted property")


def getAllNewStates(network, state):
    nextStates = set()
    transitions = network.get_transitions(state)
    for transition in transitions:
        branches = network.get_branches(state, transition)
        for branch in branches:
            nextState = network.jump(state, transition, branch)
            nextStates.add(nextState)
    return nextStates


start()

# 1 start with some printing
# 1.1 check properties
# 1.1.1 check single property
# enum with syntax of property
# 1.1.1.1 transform properties
# 1.1.1.2 check single syntax of property.

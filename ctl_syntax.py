from ctl_solver import findStatesWithUntilStepBounded, findStatesWithUntil


def checkLogicalExpression(model,checkSinglePropertyExpression,universe, network, propertyExpression):
    if propertyExpression.op == "ap":
        states = set()
        for state in universe:
            if network.get_expression_value(state, propertyExpression.args[0]):
                states.add(state)
        return states
    elif propertyExpression.op == "not":
        states = checkSinglePropertyExpression(model, universe, network, propertyExpression.args[0])
        return universe - states
    elif propertyExpression.op == "or":
        states1 = checkSinglePropertyExpression(model, universe, network, propertyExpression.args[0])
        states2 = checkSinglePropertyExpression(model, universe, network, propertyExpression.args[1])
        return states1.union(states2)
    elif propertyExpression.op == "and":
        states1 = checkSinglePropertyExpression(model, universe, network, propertyExpression.args[0])
        states2 = checkSinglePropertyExpression(model, universe, network, propertyExpression.args[1])
        return states1.intersection(states2)
    else:
        raise Exception("unsupported propertyExpression")


def checkSelectorExpression(model, checkSinglePropertyExpression, universe, network, selectorPropertyExpression):
    forAll = None
    if selectorPropertyExpression.op == "exists":
        forAll = False
    elif selectorPropertyExpression.op == "forall":
        forAll = True
    else:
        raise Exception("unsupported propertyExpression")

    propertyExpression = selectorPropertyExpression.args[0]
    if propertyExpression.op == "until":
        allowedStates = checkSinglePropertyExpression(model, universe, network, propertyExpression.args[0])
        goalStates = checkSinglePropertyExpression(model, universe, network, propertyExpression.args[1])
        return findStatesWithUntil(network, allowedStates, goalStates,goalStates, forAll)
    elif propertyExpression.op == "eventually":
        goalStates = checkSinglePropertyExpression(model, universe, network, propertyExpression.args[0])
        return findStatesWithUntil(network, universe, goalStates, goalStates, forAll)
    elif propertyExpression.op == "always":
        expression1 = model.PropertyExpression("not", [propertyExpression.args[0]])
        expression2 = model.PropertyExpression("eventually", [expression1])
        expression3 = None
        if forAll:
            expression3 = model.PropertyExpression("exists", [expression2])
        else:
            expression3 = model.PropertyExpression("forall", [expression2])

        expression4 = model.PropertyExpression("not", [expression3])
        return checkSinglePropertyExpression(model, universe, network, expression4)
    elif propertyExpression.op == "next":
        goalStates = checkSinglePropertyExpression(model, universe, network, propertyExpression.args[0])
        return findStatesWithUntilStepBounded(network, universe, goalStates, 1, set(), forAll)
    elif propertyExpression.op == "step-bounded-until":
        allowedStates = checkSinglePropertyExpression(model, universe, network, propertyExpression.args[0])
        goalStates = checkSinglePropertyExpression(model, universe, network, propertyExpression.args[1])
        return findStatesWithUntilStepBounded(network, allowedStates, goalStates, propertyExpression.args[2], goalStates, forAll)
    elif propertyExpression.op == "step-bounded-eventually":
        goalStates = checkSinglePropertyExpression(model, universe, network, propertyExpression.args[0])
        return findStatesWithUntilStepBounded(network, universe, goalStates, propertyExpression.args[1], goalStates, forAll)
    elif propertyExpression.op == "step-bounded-always":
        expression1 = model.PropertyExpression("not", [propertyExpression.args[0]])
        expression2 = model.PropertyExpression("step-bounded-eventually", [expression1, propertyExpression.args[1]])
        expression3 = None
        if forAll:
            expression3 = model.PropertyExpression("exists", [expression2])
        else:
            expression3 = model.PropertyExpression("forall", [expression2])
        expression4 = model.PropertyExpression("not", [expression3])
        return checkSinglePropertyExpression(model, universe, network, expression4)
    else:
        raise Exception("unsupported propertyExpression")


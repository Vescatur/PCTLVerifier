from pctl_solver import findStatesWithProbabilityUntil


def checkComparisonExpressions(model, checkSinglePropertyExpression, universe, network, propertyExpression):
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
        allowedStates = checkSinglePropertyExpression(model, checkSinglePropertyExpression, universe, network, pathExpression.args[0])
        goalStates = checkSinglePropertyExpression(model, checkSinglePropertyExpression, universe, network, pathExpression.args[1])
        return findStatesWithProbabilityUntil(network, universe, allowedStates, goalStates, isEquals, isLessThan, isMax,
                                              probability)
    elif pathExpression.op == "eventually":
        goalStates = checkSinglePropertyExpression(model, checkSinglePropertyExpression, universe, network, pathExpression.args[0])
        return findStatesWithProbabilityUntil(network, universe, universe, goalStates, isEquals, isLessThan, isMax,
                                              probability)
    elif pathExpression.op == "always":
        expression1 = model.PropertyExpression("not", [pathExpression.args[0]])
        expression2 = model.PropertyExpression("eventually", [expression1])
        expression3 = None
        expression4 = None
        if isMax:
            expression3 = model.PropertyExpression("p_min", [expression2])
        else:
            expression3 = model.PropertyExpression("p_max", [expression2])

        if isLessThan:
            if isEquals:
                expression4 = model.PropertyExpression(">", [expression3, 1 - probability]) # this doesn't work
            else:
                expression4 = model.PropertyExpression(">=", [expression3, 1 - probability])
        else:
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
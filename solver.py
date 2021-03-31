from ctl_syntax import checkLogicalExpression, checkSelectorExpression
from pctl_syntax import checkComparisonExpressions


def checkSingleProperty(model, universe, network, propertie, initialState):
    trueStates = checkSinglePropertyExpression(model, universe, network, propertie.exp)
    return initialState in trueStates


def checkSinglePropertyExpression(model,universe, network, propertyExpression):
    logicalExpressions = {"ap", "or", "not", "and"}
    selectorExpressions = {"exists", "forall"}
    pathExpressions = {"until", "next", "step-bounded-always", "step-bounded-eventually",
                       "step-bounded-until", "eventually", "always"}
    comparisonExpressions = {"<", ">", "<=", ">="}
    probabilityExpressions = {"p_min", "p_max"}

    op = propertyExpression.op
    if op in logicalExpressions:
        return checkLogicalExpression(model, checkSinglePropertyExpression, universe, network, propertyExpression)
    elif op in selectorExpressions:
        return checkSelectorExpression(model, checkSinglePropertyExpression, universe, network, propertyExpression)
    elif op in comparisonExpressions:
        return checkComparisonExpressions(model, checkSinglePropertyExpression, universe, network, propertyExpression)
    elif op in probabilityExpressions:
        raise Exception("incorrectly formatted property")
    elif op in pathExpressions:
        raise Exception("incorrectly formatted property")
    else:
        print(op)
        raise Exception("unsupported propertyExpression")
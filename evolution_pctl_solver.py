import math
import random

from config import PRINT_EVI_STEP, PRINT_EVI_RESULT, RANDOMNESS_OF_STEP_LOWER_BOUND, \
    RANDOMNESS_OF_STEP_UPPER_BOUND
from ctl_solver import findStatesWithUntil
from value_pctl_solver import createInitialProbabilityToReachGoal, findStatesWithCorrectProbability, stepForSingleState


def findStatesWithEvolutionValueIteration(network, universe, allowedStates, goalStates, isEquals, isLessThan, isMax,
                                          probabilityTarget):
    notBmecAllowedStates = findStatesWithUntil(network, allowedStates, goalStates, set(), False)

    distribution = findDistributionWithEvolutionValueIteration(network, universe, notBmecAllowedStates, goalStates,
                                                               isMax)
    if PRINT_EVI_RESULT:
        printDistribution(universe, distribution)
    returnStates = findStatesWithCorrectProbability(goalStates, notBmecAllowedStates, distribution, probabilityTarget,
                                                    isLessThan, isEquals)
    return returnStates




def findDistributionWithEvolutionValueIteration(network, universe, allowedStates, goalStates, isMax):
    numberOfDistributions = 50
    distributions = [None] * numberOfDistributions
    scores = [None] * numberOfDistributions
    differenceDistribution = [None] * numberOfDistributions

    for i in range(0, numberOfDistributions):
        distributions[i] = createRandomDistribution(universe, allowedStates, goalStates)

    for i in range(1, 1000):
        for i in range(0, numberOfDistributions):
            differenceDistribution[i] = calculateDifferenceDistributionOfDistribution(universe, network, allowedStates, goalStates, isMax, distributions[i])
            scores[i] = calculateScoreOfDifferenceDistribution(allowedStates, differenceDistribution[i])

        orderedDistribution = orderDistributions(numberOfDistributions, scores, distributions)

        distributions = [None] * numberOfDistributions
        copiedDistributions = math.floor(numberOfDistributions / 2)
        for i in range(0, copiedDistributions):
            distributions[i] = orderedDistribution[i]

        for i in range(copiedDistributions, numberOfDistributions):
            firstRandom = random.randint(0, copiedDistributions - 1)
            secondRandom = random.randint(0, copiedDistributions - 2)
            if secondRandom >= firstRandom:
                secondRandom = secondRandom + 1
            firstDistribution = orderedDistribution[firstRandom]
            secondDistribution = orderedDistribution[secondRandom]
            distributions[i] = createCombinedDistribution(universe, allowedStates, goalStates, firstDistribution,
                                                          secondDistribution, scores[firstRandom], scores[secondRandom],
                                                          differenceDistribution[firstRandom],
                                                          differenceDistribution[secondRandom])

        if PRINT_EVI_STEP:
            printDistributions(universe, distributions)
    return distributions[0]


def createCombinedDistribution(universe, allowedStates, goalStates, firstDistribution, secondDistribution, scoreFirst, scoreSecond, stepFirst, stepSecond):
    randomAllowance = 0.1
    newDistribution = createInitialProbabilityToReachGoal(universe, goalStates)
    distanceFirst = math.sqrt(scoreFirst)
    distanceSecond = math.sqrt(scoreSecond)
    firstStep = random.uniform(0, RANDOMNESS_OF_STEP_UPPER_BOUND-RANDOMNESS_OF_STEP_LOWER_BOUND)+RANDOMNESS_OF_STEP_LOWER_BOUND
    secondStep = random.uniform(0, RANDOMNESS_OF_STEP_UPPER_BOUND-RANDOMNESS_OF_STEP_LOWER_BOUND)+RANDOMNESS_OF_STEP_LOWER_BOUND
    for state in allowedStates:
        if state not in goalStates:
            firstProbability = firstDistribution[state]
            secondProbability = secondDistribution[state]

            difference = abs(firstProbability - secondProbability)
            if difference == 0:
                difference = 0.1
            highestProbability = max(firstProbability, secondProbability)
            lowestProbability = min(firstProbability, secondProbability)

            #This chooses a random position between first and the second distributions
            upperRandom = highestProbability + (difference * randomAllowance)
            lowerRandom = lowestProbability - (difference * randomAllowance)
            # newDistribution[state] = max(0,min(1,random.uniform(lowerRandom,upperRandom)))
            newDistribution[state] = random.uniform(lowerRandom, upperRandom)

            #This adds the direction in which the distributions are moving towards. It is scaled to the difference between the points.
            if distanceFirst != 0 and distanceSecond != 0:
                newDistribution[state] = newDistribution[state] + \
                                     stepFirst[state]/distanceFirst*firstStep*difference + \
                                     stepSecond[state]/distanceSecond*secondStep*difference

    return newDistribution


def orderDistributions(numberOfDistributions, scores, distributions):
    scoreDistributions = [None] * numberOfDistributions
    for i in range(0, numberOfDistributions):
        scoreDistributions[i] = (scores[i], distributions[i])
    orderedScoreDistributions = sorted(scoreDistributions, key=lambda x: x[0])

    orderedDistribution = [None] * numberOfDistributions
    for i in range(0, numberOfDistributions):
        orderedDistribution[i] = orderedScoreDistributions[i][1]
    return orderedDistribution


def calculateDifferenceDistributionOfDistribution(universe, network, allowedStates, goalStates, isMax, distribution):
    nextDistribution = stepForDistribution(universe, network, allowedStates, goalStates, isMax, distribution)
    differenceDistribution = dict()
    for state in allowedStates:
        differenceDistribution[state] = nextDistribution[state] - distribution[state]
    return differenceDistribution


def stepForDistribution(universe, network, allowedStates, goalStates, isMax, distribution):
    newDistribution = createInitialProbabilityToReachGoal(universe, goalStates)
    for stateFrom in allowedStates:
        if stateFrom in goalStates:
            continue
        outerProbability = stepForSingleState(network, stateFrom, distribution, isMax)
        newDistribution[stateFrom] = outerProbability
    return newDistribution


def calculateScoreOfDifferenceDistribution(allowedStates, differenceDistribution):
    score = 0
    for state in allowedStates:
        score += differenceDistribution[state] * differenceDistribution[state]
    return score


def createRandomDistribution(universe, allowedStates, goalStates):
    distribution = dict()
    for state in universe:
        distribution[state] = 0
    for state in allowedStates:
        distribution[state] = random.uniform(0, 1)
    for state in goalStates:
        distribution[state] = 1
    return distribution


def printDistribution(universe, distribution):
    print("---")
    for state in universe:
        print(str(state) + " " + str(distribution[state]))


def printDistributions(universe, distributions):
    print("---")
    for state in universe:
        print(str(state), end='')
        for distribution in distributions:
            print(" " + str(distribution[state]), end='')
        print("")
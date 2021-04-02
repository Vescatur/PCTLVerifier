import math
import random

from ctl_solver import findStatesWithUntil
from pctl_solver import createInitialProbabilityToReachGoal, findStatesWithCorrectProbability, stepForSingleState

def printDistribution(universe,distribution):
    print("---")
    for state in universe:
        print(str(state) + " " + str(distribution[state]))


def printDistributions(universe,distributions):
    print("---")
    for state in universe:
        print(str(state),end='')
        for distribution in distributions:
            print(" "+str(distribution[state]),end='')
        print("")


def findStatesWithEvolutionValueIteration(network, universe, allowedStates, goalStates, isEquals, isLessThan, isMax, probabilityTarget):
    notBmecAllowedStates = findStatesWithUntil(network, allowedStates, goalStates, set(), False)


    #check welke states bij goal kan komen. Zet die in allowed States.
    #check of er een mec is. Gooi dan een exception.


    distribution = findDistributionWithEvolutionValueIteration(network, universe, notBmecAllowedStates, goalStates, isMax)
    printDistribution(universe, distribution)
    returnStates = findStatesWithCorrectProbability(goalStates,notBmecAllowedStates,distribution,probabilityTarget,isLessThan,isEquals)
    return returnStates


def copyDistribution(universe, distribution):
    newDistribution = dict()
    for state in universe:
        newDistribution[state] = distribution[state]
    return newDistribution


def findDistributionWithEvolutionValueIteration(network, universe, allowedStates, goalStates, isMax):
    numberOfDistributions = 50
    distributions = [None]*numberOfDistributions
    scores = [None]*numberOfDistributions
    for i in range(0,numberOfDistributions):
        distributions[i] = createRandomDistribution(universe, allowedStates, goalStates)

    for i in range(1,1000):
        for i in range(0,numberOfDistributions):
            scores[i] = calculateScoreOfDistribution(universe, network, allowedStates, goalStates, isMax, distributions[i])
        orderedDistribution = [x for _,x in sorted(zip(scores,distributions))]
        distributions = [None]*numberOfDistributions
        copiedDistributions = math.floor(numberOfDistributions/2)
        for i in range(0,copiedDistributions):
            distributions[i] = orderedDistribution[i]

        for i in range(copiedDistributions, numberOfDistributions):
            firstDistribution = orderedDistribution[random.randint(0,copiedDistributions-1)]
            secondDistribution = orderedDistribution[random.randint(0,copiedDistributions-1)]
            distributions[i] = createCombinedDistribution(universe, allowedStates, goalStates, firstDistribution, secondDistribution)

        #highestDistribution = copyDistribution(universe, distributions[0])
        #lowestDistribution = copyDistribution(universe, distributions[0])
        #for i in range(1,numberOfDistributions):
        #    distribution = orderedDistribution[i]
        #    for state in universe:
        #        highestDistribution[state] = max(highestDistribution[state],distribution[state])
        #        lowestDistribution[state] = min(lowestDistribution[state],distribution[state])

        #for i in range(copiedDistributions, numberOfDistributions):
        #   distributions[i] = createCombinedDistribution(universe, allowedStates, goalStates, lowestDistribution, highestDistribution)

        #print("distributions")
        #printDistributions(universe,distributions)
        #for i in range(0, numberOfDistributions):
        #    print(distributions[i])
    return distributions[0]


def createRandomDistribution(universe, allowedStates, goalStates):
    distribution = dict()
    for state in universe:
        distribution[state] = 0
    for state in allowedStates:
        distribution[state] = random.uniform(0, 1)
    for state in goalStates:
        distribution[state] = 1
    return distribution


def createCombinedDistribution(universe, allowedStates, goalStates, firstDistribution, secondDistribution):
    randomAllowance = 0.1
    newDistribution = createInitialProbabilityToReachGoal(universe, goalStates)
    for state in allowedStates:
        if state not in goalStates:
            firstProbability = firstDistribution[state]
            secondProbability = secondDistribution[state]

            difference = abs(firstProbability-secondProbability)
            if difference == 0:
                difference = 0.1
            highestProbability = max(firstProbability,secondProbability)
            lowestProbability = min(firstProbability,secondProbability)

            upperRandom = highestProbability+(difference*randomAllowance)
            lowerRandom = lowestProbability-(difference*randomAllowance)
            #newDistribution[state] = max(0,min(1,random.uniform(lowerRandom,upperRandom)))
            newDistribution[state] = random.uniform(lowerRandom,upperRandom)
    return newDistribution


def calculateScoreOfDistribution(universe, network, allowedStates, goalStates, isMax, distribution):
    nextDistribution = stepForDistribution(universe, network, allowedStates, goalStates, isMax, distribution)
    score = 0
    for state in allowedStates:
        difference = abs(distribution[state]-nextDistribution[state])
        score += difference*difference
    return score


def stepForDistribution(universe, network, allowedStates, goalStates, isMax, distribution):
    newDistribution = createInitialProbabilityToReachGoal(universe, goalStates)
    for stateFrom in allowedStates:
        if stateFrom in goalStates:
            continue
        outerProbability = stepForSingleState(network,stateFrom,distribution, isMax)
        newDistribution[stateFrom] = outerProbability
    return newDistribution


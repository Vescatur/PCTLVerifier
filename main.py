import sys
from importlib import util
from timeit import default_timer as timer

from solver import checkSingleProperty

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
    #for i in range(len(network.properties)):
    i = 0
    start_time = timer()
    propertie = network.properties[i]
    result = checkSingleProperty(model,universe, network, propertie, initialState)
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

start()

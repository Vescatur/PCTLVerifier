# Userguide of CTL and PCTL verifier

To see this document with formatting, go to https://github.com/Vescatur/PCTLVerifier.

This project is made for subject Software Science on the university of Utwente. This program is able to verify ctl and pctl properties. The modest toolkit is used to generate the models and properties. https://www.modestchecker.net/

This document contains an explanation on how to use the tool, the property syntax that it supports, the algorithms it uses, performance statistics, and a description of the file structure.

## Run it
The main.py is the entrypoint of the application. The only argument is the file from the python export. There are no libraries required. There are some settings related to the algorithm these will be discussed in the chapter "Algorithms and Performance". The settings can be changed in the file config.py.

    python main.py "example.py"

## PCTL and CTL properties
Below is the supported syntax. The syntax has been split up into groups. The options are separated by a |. A property must start with p.

    p = logicalExpressions | selectorExpressions pathExpressions | selectorExpressions boundedPathExpressions | probabilityExpressions(pathExpressions) comparisonExpressions number
    logicalExpressions = ap | p or p | not p | p and p
    selectorExpressions = exists | forall
    pathExpressions = p until p | eventually p | always p
    boundedPathExpressions = next | step-bounded-always | step-bounded-eventually | step-bounded-until
    comparisonExpressions = < | > | <= | >=
    probabilityExpressions = p_min | p_max

As described above, ctl computed bounded and unbounded properties. For pctl only unbounded properties are supported. There has been no split between ctl and pctl properties. The verifier wil use ctl or pctl algorithms based on the context.


## Algorithms and Performance

### CTL
The logicalExpressions have been implemented by the set operations. The CTL properties are solved using Gauss-Seidel method or a step algorithm.

#### Performance
The file benchMark.modest has been used to test the speed. The settings used are stepSize = 2 and bound = 65536.

|             	| Gauss-Seidel 	| Step 	|
|-------------	|--------------	|------	|
| E<>(finish) 	| 1,89         	| 3,46 	|
| A<>(finish) 	| 2,81         	| 3,32 	|

### PCTL
The PCTL properties can be solved using three different algorithms Value Iteration, Optimistic Value Iteration and Evolution Value Iteration. The Evolution Value Iteration algorithm assumes that the model does not contain any MECs.


The algorithm can selected in the config.py file. Turn one of the values to true to select an algorithm. If both are false then Value Iteration is used.

    USE_OPTIMISTIC_VALUE_ITERATION = False
    USE_EVOLUTION_VALUE_ITERATION = False

#### Performance

|                                    	| Modest VI              	| VI                      	| Modest OVI 	| OVI      	| EVI                      	|
|------------------------------------	|------------------------	|-------------------------	|------------	|----------	|--------------------------	|
| Coinflip                           	| 0.0                    	| 0.00022                 	| 0.0        	| 0.00038  	| 0.068                    	|
| self loop 0.99999                  	| 0.0                    	| 0.13 (result incorrect) 	| 0.0        	| 14.2     	| 0.016                    	|
| self loop 0.9999999                	| 0.1 (result incorrect) 	| 0.14 (result incorrect) 	| 1.0        	| too long 	| 0.02                     	|
| betting money=BOUND (contains MEC) 	| 0.0                    	| 0.0                     	| 0.0        	| 5.5      	| 17.75 (result incorrect) 	|

The algorithms have been tested on four different models. For VI and OVI the time compared to Modest is also shown. The first model was a coinflip. It is a simple model. EVI takes significantly longer compared to the other algorithms. 
The next two models are with a high self loop. EVI is better with computing these. VI gives incorrect results. The implementation of OVI in modest is more efficient than my implementation.
The last model has a MEC which causes an incorrect result with the EVI algorithm.

#### Config

The following values are related to all algorithms

    ERROR_TARGET = 0.0001

The following value is related to OVI.
   
    UPPER_BOUND_HEURISTIC = 0.0001

The following values are related to EVI.

    RANDOMNESS_OUTSIDE_OF_DISTRIBUTIONS = 1
    RANDOMNESS_OF_STEP_LOWER_BOUND = 1
    RANDOMNESS_OF_STEP_UPPER_BOUND = 1.5
    NUMBER_OF_DISTRIBUTIONS = 30

You can also change how much is printed to the console, but the defaults do not need to be changed.

    PRINT_VI_RESULT = True
    PRINT_OVI_ERROR_BOUNDS = True
    PRINT_EVI_STEP = False
    PRINT_EVI_RESULT = True

## File structure
The entrypoint of the program is main.py. This file is responsible for loading the model. The files ending with _syntax.py are responsible for parsing the properties and calling the right algorithms. main_syntax.py is the entry point for parsing a property. The algorithms are in the files ending with _solver.py.
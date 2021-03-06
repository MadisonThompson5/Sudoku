import filereader
import gameboard
import variable
import domain
import trail
import constraint
import constraintnetwork
import time


#dictionary mapping heuristic to number
'''
for example, to set the variable selection heuristic to MRV,
you would say,
self.setVariableSelectionHeuristic(VariableSelectionHeuristic['MinimumRemainingValue'])
this is needed when you have more than one heuristic to break ties or use one over the other in precedence.
you can also manually set the heuristics in the main.py file when reading the parameters
as the primary heuristics to use and then break ties within the functions you implement
It follows similarly to the other heuristics and chekcs
'''
VariableSelectionHeuristic = {'None': 0, 'MRV': 1, 'DH': 2}
ValueSelectionHeuristic = {'None': 0, 'LCV': 1}
ConsistencyCheck = {'None': 0, 'ForwardChecking': 1, 'ArcConsistency': 2}
HeuristicCheck = {'None': 0, 'NKP': 1, 'NKT': 2}


class BTSolver:
    "Backtracking solver"

    ######### Constructors Method #########
    def __init__(self, gb):
        self.network = filereader.GameBoardToConstraintNetwork(gb)
        self.trail = trail.masterTrailVariable
        self.hassolution = False
        self.gameboard = gb

        self.numAssignments = 0
        self.numBacktracks = 0
        self.preprocessing_startTime = 0
        self.preprocessing_endTime = 0
        self.startTime = None
        self.endTime = None

        self.varHeuristics = 0  # refers to which variable selection heuristic in use(0 means default, 1 means MRV, 2 means DEGREE)
        self.valHeuristics = 0  # refers to which value selection heuristic in use(0 means default, 1 means LCV)
        self.cChecks = 0  # refers to which consistency check will be run(0 for backtracking, 1 for forward checking, 2 for arc consistency)
        self.heuristicChecks = 0
        # self.runCheckOnce = False
        self.tokens = []  # tokens(heuristics to use)

    ######### Modifiers Method #########


    def setTokens(self, tokens):
        ''' set the set of heuristics to be taken into consideration'''
        self.tokens = tokens

    def setVariableSelectionHeuristic(self, vsh):
        '''modify the variable selection heuristic'''
        self.varHeuristics = vsh

    def setValueSelectionHeuristic(self, vsh):
        '''modify the value selection heuristic'''
        self.valHeuristics = vsh

    def setConsistencyChecks(self, cc):
        '''modify the consistency check'''
        self.cChecks = cc

    def setHeuristicChecks(self, hc):
        '''modify the heurisic check (naked pairs and triples)'''
        self.heuristicChecks += hc

    ######### Accessors Method #########
    def getSolution(self):
        return self.gameboard

    # @return time required for the solver to attain in seconds
    def getTimeTaken(self):
        return self.endTime - self.startTime

    ######### Helper Method #########
    def checkConsistency(self):
        '''which consistency check to run but it is up to you when implementing the heuristics to break ties using the other heuristics passed in'''
        if self.cChecks == 0:
            return self.assignmentsCheck()
        elif self.cChecks == 1:
            return self.forwardChecking()
        elif self.cChecks == 2:
            return self.arcConsistency()
        else:
            return self.assignmentsCheck()

    def checkHeuristics(self):
        if self.heuristicChecks == 1:
            return self.nakedPairs()
        elif self.heuristicChecks == 2:
            return self.nakedTriples()
        elif self.heuristicChecks == 3:
            return self.nakedPairs() and self.nakedTriples()
        else:
            return True    

    def assignmentsCheck(self):
        """
            default consistency check. Ensures no two variables are assigned to the same value.
            @return true if consistent, false otherwise.
        """
        for v in self.network.variables:
            if v.isAssigned():
                for vOther in self.network.getNeighborsOfVariable(v):
                    if v.getAssignment() == vOther.getAssignment():
                        return False
        return True

    def nakedPairs(self):
        """
           TODO: Implement naked pairs heuristic.
        """
        i = 0
        variables = self.network.variables
        while ( i < len(variables)):
            if not variables[i].isAssigned():
                if(variables[i].domain.size() == 2):
                    saved_domains = [variables[i]]
                    for v in self.network.getNeighborsOfVariable(variables[i]):
                        if v.domain.size() == 2:
                            for values in v.domain.values:
                                is_same = True
                                if not variables[i].domain.contains(values):
                                    is_same = False
                                if is_same:
                                    saved_domains.append(v)
                    if len(saved_domains) > 2:
                        return false
                    if len(saved_domains) == 2:
                       for v1 in self.network.getNeighborsOfVariable(variables[i]):
                           if not saved_domains.contains(v1):
                               for values in variables[i].domain:
                                   v1.removeValueFromDomain(values)
                                   if v1.domain.size() == 0:
                                       return False
            i += 1
        return True


    def nakedTriples(self):
        """
           TODO:  Implement naked triples heuristic.
        """
        i = 0
        variables = self.network.variables
        while ( i < len(variables)):
            if not variables[i].isAssigned():
                if(variables[i].domain.size() == 3):
                    saved_domains = [variables[i]]
                    for v in self.network.getNeighborsOfVariable(variables[i]):
                        if v.domain.size() <= 3:
                            for values in v.domain.values:
                                is_same = True
                                if not variables[i].domain.contains(values):
                                    is_same = False
                                if is_same:
                                    saved_domains.append(v)
                    if len(saved_domains) > 3:
                        return false
                    if len(saved_domains) == 2:
                       for v1 in self.network.getNeighborsOfVariable(variables[i]):
                           if not saved_domains.contains(v1):
                               for values in variables[i].domain:
                                   v1.removeValueFromDomain(values)
                                   if v1.domain.size() == 0:
                                       return False
            i += 1
        return True 


    def forwardChecking(self):
        i= 0;
        variables = self.network.variables
        while ( i < len(variables)):
            if variables[i].isAssigned():

                for v in self.network.getNeighborsOfVariable(variables[i]):
                    if variables[i].getAssignment() == v.getAssignment():
                        return False

                    v.removeValueFromDomain(variables[i].getAssignment())

                    if v.domain.size() == 0:
                        return False
            i +=1

        return True



    def arcConsistency(self):
        i= 0;
        variables = self.network.variables
        while ( i < len(variables)):
            if variables[i].isAssigned():
                for x in self.network.getNeighborsOfVariable(variables[i]):
                    if variables[i].getAssignment() == x.getAssignment():
                        return False
                    x.removeValueFromDomain(variables[i].getAssignment())
                    if x.domain.size() == 0:
                        return False
                for v1 in self.network.variables:
                    if v1.isAssigned():
                        for x1 in self.network.getNeighborsOfVariable(v1):
                            if v1.getAssignment() == x1.getAssignment():
                                return False
                            x1.removeValueFromDomain(v1.getAssignment())
                            if x1.domain.size() == 0:
                                return False
                i+=1
        return True
                
        """
            TODO: Implement Maintaining Arc Consistency.
        """

    def selectNextVariable(self):
        """
            Selects the next variable to check.
            @return next variable to check. null if there are no more variables to check.
        """
        if self.varHeuristics == 0:
            return self.getfirstUnassignedVariable()
        elif self.varHeuristics == 1:
            return self.getMRV()
        elif self.varHeuristics == 2:
            return self.getDegree()
        else:
            return self.getfirstUnassignedVariable()

    def getfirstUnassignedVariable(self):
        """
            default next variable selection heuristic. Selects the first unassigned variable.
            @return first unassigned variable. null if no variables are unassigned.
        """
        for v in self.network.variables:
            if not v.isAssigned():
                return v
        return None

    def getMRV(self):
        to_return = None
        mrv = float('inf')
        for v in self.network.variables:
            if v.isAssigned():
                pass
            else:
                if v.domain.size() < mrv:
                    to_return = v
                    mrv= v.domain.size()
        return to_return
                
            

        """
            TODO: Implement MRV heuristic
            @return variable with minimum remaining values that isn't assigned, null if all variables are assigned.
        """

    def getDegree(self):
        to_return= None
        muv= float("-inf")
        for v in self.network.variables:
            if v.isAssigned():
                pass

            if not v.isAssigned():
                neighbors= self.network.getNeighborsOfVariable(v)

                num= 0
                for x in neighbors:
                    if not x.isAssigned():
                        num+= 1
                if muv < num:
                    to_return = v
                    muv= num
        return to_return
                
        
        """
            TODO: Implement Degree heuristic
            @return variable constrained by the most unassigned variables, null if all variables are assigned.
        """
         
      

    def getNextValues(self, v):
        """
            Value Selection Heuristics. Orders the values in the domain of the variable
            passed as a parameter and returns them as a list.
            @return List of values in the domain of a variable in a specified order.
        """
        if self.valHeuristics == 0:
            return self.getValuesInOrder(v)
        elif self.valHeuristics == 1:
            return self.getValuesLCVOrder(v)
        else:
            return self.getValuesInOrder(v)


    def getValuesInOrder(self, v):
        """
            Default value ordering.
            @param v Variable whose values need to be ordered
            @return values ordered by lowest to highest.
        """
        values = v.domain.values
        return sorted(values)

    

    
    def getValuesLCVOrder(self, v):
        def compare( x1, x2):
            num1 = 0
            num2 = 0
            for x in self.network.getNeighborsOfVariable(v):    
                if x.domain.contains(x2):
                    num2+= 1
                if x.domain.contains(x1):
                    num1+= 1
            return num1- num2

        vals = v. domain.values
        to_return  = sorted(vals, compare)
        return to_return
        
        """
            TODO: LCV heuristic
        """
        

    def success(self):
        """ Called when solver finds a solution """
        self.hassolution = True
        self.gameboard = filereader.ConstraintNetworkToGameBoard(self.network,
                                                                 self.gameboard.N,
                                                                 self.gameboard.p,
                                                                 self.gameboard.q)


    ######### Solver Method #########
    def solve(self):
        """ Method to start the solver """
        self.startTime = time.time()
        # try:
        self.solveLevel(0)
        # except:
        # print("Error with variable selection heuristic.")
        self.endTime = time.time()
        # trail.masterTrailVariable.trailStack = []
        self.trail.trailStack = []


    def solveLevel(self, level):
        """
            Solver Level
            @param level How deep the solver is in its recursion.
            @throws VariableSelectionException
        contains some comments that can be uncommented for more in depth analysis
        """
        # print("=.=.=.=.=.=.=.=.=.=.=.=.=.=.=.=")
        # print("BEFORE ANY SOLVE LEVEL START")
        # print(self.network)
        # print("=.=.=.=.=.=.=.=.=.=.=.=.=.=.=.=")

        if self.hassolution:
            return

        # Select unassigned variable
        v = self.selectNextVariable()
        # print("V SELECTED --> " + str(v))

        # check if the assigment is complete
        if (v == None):
            # print("!!! GETTING IN V == NONE !!!")
            for var in self.network.variables:
                if not var.isAssigned():
                    raise ValueError("Something happened with the variable selection heuristic")
            self.success()
            return

        # loop through the values of the variable being checked LCV
        # print("getNextValues(v): " + str(self.getNextValues(v)))
        for i in self.getNextValues(v):
            # print("next value to test --> " + str(i))
            self.trail.placeTrailMarker()

            # check a value
            # print("-->CALL v.updateDomain(domain.Domain(i)) to start to test next value.")
            v.updateDomain(domain.Domain(i))
            self.numAssignments += 1

            # move to the next assignment
            if self.checkConsistency() and self.checkHeuristics():
                self.solveLevel(level + 1)

            # if this assignment failed at any stage, backtrack
            if not self.hassolution:
                # print("=======================================")
                # print("AFTER PROCESSED:")
                # print(self.network)
                # print("================ ")
                # print("self.trail before revert change: ")
                for i in self.trail.trailStack:
                    pass
                    # print("variable --> " + str(i[0]))
                    # print("domain backup --> " + str(i[1]))
                # print("================= ")

                self.trail.undo()
                self.numBacktracks += 1
                # print("REVERT CHANGES:")
                # print(self.network)
                # print("================ ")
                # print("self.trail after revert change: ")
                for i in self.trail.trailStack:
                    pass
                    # print("variable --> " + str(i[0]))
                    # print("domain backup --> " + str(i[1]))
                # print("================= ")

            else:
                return


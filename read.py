import sys
import copy

# Latency dictionary
latency = {
    "add":      1,
    "sub":      1,
    "mult":     3,
    "div":      3,
    "load":     5,
    "loadI":    1,
    "loadAI":   5,
    "loadAO":   5,
    "store":    5,
    "storeAI":  5,
    "storeAO":  5,
    "outputAI": 1
    }

def main():
    # Make sure everything is in proper format
    if len(sys.argv) != 4:
        print("Improper input format:\n\"-(a,b,c) filename outputName\"")
        exit()
    # Read in parameters
    strategy, filename, outputName = sys.argv[1:]

    # Open instruction file
    fileIn = open(filename)

    # Create dependency graph from file
    depGraph = createDepenGraph(fileIn)
    
    # Print out graph
    #for i in depGraph:
    #    print(i)

    # Run specific schedulers on graph
    if strategy == "-a":
        output = a(depGraph)
    elif strategy == "-b":
        output = b(depGraph)
    elif strategy == "-c":
        output = c(depGraph)
    else:
        print("Invalid scheduler specified\n-(a,b,c) are accepted")

    #print(output)
    # Write scheduled code to scheduler
    outputFile = open(outputName, "w")
    outputFile.write(output)
    print("Output file written successfully")


class node:
    def __init__(self, line, inst, original):
        self.line = line
        self.inst = inst
        self.children = {}
        self.parents = {}
        self.latencyPath = 0
        self.originalText = original

    def addChild(self, childName, child):
        self.children[childName] = child

    def addParent(self, parentName, parent):
        self.parents[parentName] = parent
        
    def __str__(self):
        return str(self.line) + " - Children: " + str(self.children) + "\nParents: " + str(self.parents) + "\n"

arithmetic = ["add", "sub", "mult", "div"]


def createDepenGraph(fileIn):
    read = {}
    write = {}
    nodes = []
    for index, originalLine in enumerate(fileIn):
    
        # Strip commas, remove '=>' and split
        line = [i.strip(",") for i in originalLine.replace('=>','').split()]
        instruction = line[0]
        
        # Create node of dependency graph
        curr = node(index, instruction, originalLine)

        ## Arithmetic instructions
        ## inst param1 param2 => param3
        if instruction in arithmetic:
            param1, param2, param3 = line[1:]
            
            # True check
            if param1 in write:
                temp = write[param1].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])
            if param2 in write:
                temp = write[param2].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])
                
            # Anti check
            if param3 in read:
                temp = read[param3].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])
            
            # update read/ write dict
            read[param1] = curr
            read[param2] = curr
            write[param3] = curr

        ## load instruction
        ## inst param1 => param2
        if instruction == "load":
            param1, param2 = line[1:]
            # True check
            if param1 in write:
                temp = write[param1].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])

            # Anti check
            if param2 in read:
                temp = read[param2].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])
            
            # update read/ write dict
            read[param1] = curr
            write[param2] = curr
            
        ## loadI Instruction
        ## inst immediate => param1
        if instruction == "loadI":
            param1 = line[2]

            # Anti check
            if param1 in read:
                temp = read[param1].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])
            
            # update read/ write dict
            write[param1] = curr
        
        ## loadAI instruction
        ## inst param1 immediate => param2
        if instruction == "loadAI":
            param1, imm, param2 = line[1:]
            # True check
            if param1 in write:
                temp = write[param1].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])
            if param1 + imm in write:
                temp = write[param1 + imm].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])

            # Anti check
            if param2 in read:
                temp = read[param2].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])
            
            # update read/ write dict
            read[param1] = curr
            read[param1 + imm] = curr
            write[param2] = curr
        
        ## loadAO instruction
        ## inst param1 immediate => param2
        if instruction == "loadAO":
            param1, param2, param3 = line[1:]
            # True check
            if param1 in write:
                temp = write[param1].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])
            if param2 in write:
                temp = write[param2].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])

            # Anti check
            if param3 in read:
                temp = read[param3].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])
            
            # update read/ write dict
            read[param1] = curr
            read[param2] = curr
            write[param3] = curr
        
        ## store Instruction
        ## inst param1 => param2
        if instruction == "store":
            param1, param2 = line[1:]
            # True check
            if param1 in write:
                temp = write[param1].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])

            if param2 in write:
                temp = write[param2].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])
            
            # update read/ write dict
            read[param1] = curr
            read[param2] = curr
            
        ## storeAI Instruction
        ## inst param1 => param2
        if instruction == "storeAI":
            param1, param2, imm = line[1:]
            # True check
            if param1 in write:
                temp = write[param1].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])

            if param2 in write:
                temp = write[param2].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])
            
            if param2 + imm in write:
                temp = write[param2 + imm].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])
            # update read/ write dict
            read[param1] = curr
            read[param2] = curr
            write[param2 + imm] = curr
            
        ## storeAO Instruction
        ## inst param1 => param2
        if instruction == "storeAO":
            param1, param2, param3 = line[1:]
            # True check
            if param1 in write:
                temp = write[param1].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])

            if param2 in write:
                temp = write[param2].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])
            
            if param3 in write:
                temp = write[param3].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])   
                         
            # update read/ write dict
            read[param1] = curr
            read[param2] = curr              
            read[param3] = curr
                   
        ## outputAI Instruction
        ## inst param1 immediate
        if instruction == "outputAI":
            param1, imm = line[1:]
            # True check
            if param1 in write:
                temp = write[param1].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])
                
            if param1 + imm in write:
                temp = write[param1 + imm].line
                nodes[temp].addChild(index, curr)
                curr.addParent(temp, nodes[temp])
                         
            # update read/ write dict
            read[param1] = curr
            read[param1 + imm] = curr
            
        nodes.append(curr)
    
    return nodes

## longest latency-weighted path to root
def a(depGraph):
    depGraph = countLatencies(depGraph)
    
    #for i in depGraph:
    #    print(str(i.line) + " " + str(i.latencyPath))
    
    schedule = {}
    done = set()
    
    cycle = 0
    ready = []
    for i in depGraph:
        if i.parents == {}:
            ready.append(i)
            
    active = []
    
    while ready != [] or active != []:
        if ready != []:
        
            # Remove highest priority
            operation = max(ready, key=lambda x:x.latencyPath)
            ready.remove(operation)
            
            schedule[operation.line] = cycle
            active.append(operation)
            
        cycle = cycle + 1
          
        for op in active:
            if schedule[op.line] + latency[op.inst] <= cycle:
                active.remove(op)
                done.add(op.line)

                for line, child in op.children.items():
                    # Check if child is ready by checking if all parents are done
                    isReady = True
                    for key, parent in child.parents.items():
                        if parent.line not in done:
                            isReady = False
                    if isReady:
                        ready.append(child)
                        
    ## Create output text from schedule
    output = ""
    while schedule != {}:
        text = min(schedule, key=schedule.get)
        output = output + depGraph[text].originalText
        del schedule[text]
        
    return output

def countLatencies(graph):
    graph[-1].latencyPath = latency[graph[-1].inst]
    stack = [graph[-1].line]
    while stack != []:
        line = stack.pop(0)
        lat = graph[line].latencyPath
        for parentLine in graph[line].parents:
            newParentLat = lat + latency[graph[parentLine].inst]
            if graph[parentLine].latencyPath <  newParentLat:
                graph[parentLine].latencyPath =  newParentLat
            stack.append(parentLine)
        
    return graph

## Highest latency instruction
def b(depGraph):

    schedule = {}
    done = set()
    
    cycle = 0
    ready = []
    for i in depGraph:
        if i.parents == {}:
            ready.append(i)
            
    active = []
    
    while ready != [] or active != []:
        if ready != []:
        
            # Remove highest priority
            operation = max(ready, key=lambda x:latency[x.inst])
            ready.remove(operation)
            
            schedule[operation.line] = cycle
            active.append(operation)
            
        cycle = cycle + 1
          
        for op in active:
            if schedule[op.line] + latency[op.inst] <= cycle:
                active.remove(op)
                done.add(op.line)

                for line, child in op.children.items():
                    # Check if child is ready by checking if all parents are done
                    isReady = True
                    for key, parent in child.parents.items():
                        if parent.line not in done:
                            isReady = False
                    if isReady:
                        ready.append(child)
                        
    ## Create output text from schedule
    output = ""
    while schedule != {}:
        text = min(schedule, key=schedule.get)
        output = output + depGraph[text].originalText
        del schedule[text]
        
    return output

def c(depGraph):
    
    depGraph = countDescendants(depGraph)
    schedule = {}
    done = set()
    
    cycle = 0
    ready = []
    for i in depGraph:
        if i.parents == {}:
            ready.append(i)
            
    active = []
    
    while ready != [] or active != []:
        if ready != []:
        
            # Remove highest priority
            operation = max(ready, key=lambda x:x.latencyPath)
            ready.remove(operation)
            
            schedule[operation.line] = cycle
            active.append(operation)
            
        cycle = cycle + 1
          
        for op in active:
            if schedule[op.line] + latency[op.inst] <= cycle:
                active.remove(op)
                done.add(op.line)

                for line, child in op.children.items():
                    # Check if child is ready by checking if all parents are done
                    isReady = True
                    for key, parent in child.parents.items():
                        if parent.line not in done:
                            isReady = False
                    if isReady:
                        ready.append(child)
                        
    ## Create output text from schedule
    output = ""
    while schedule != {}:
        text = min(schedule, key=schedule.get)
        output = output + depGraph[text].originalText
        del schedule[text]
        
    return output
    
def countDescendants(graph):
    graph[-1].latencyPath = 0
    stack = [graph[-1].line]
    while stack != []:
        line = stack.pop(0)
        lat = graph[line].latencyPath
        for parentLine in graph[line].parents:
            graph[parentLine].latencyPath = graph[parentLine].latencyPath + lat + 1
            stack.append(parentLine)
        
    return graph

if __name__ == "__main__":
    main()

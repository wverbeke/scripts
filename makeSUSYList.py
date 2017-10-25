import sys
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')

import os

from rest import *


def findLink(notes): 
    for l in notes.splitlines():
        if "https" in l:
            return l
    return ""

def goodFragment(fragment):
    if "Constructing grid" in fragment:
        return True
    else:
        return False

def occursFirst(text, strings):
    for l in text.splitlines():
        for s in strings:
            if s in l:
                return s
    return ""

def findCode(fragment):
    code = ""
    toAdd = False
    beginnings = ["model = ", "# weighted average of matching", "# Parameters that define the grid", "# Fit to", "class ",  "# Number of events"]
    beginString = occursFirst(fragment, beginnings)
    for l in fragment.splitlines():
        if beginString in l:
            toAdd = True
        elif "for point in mpoints" in l:
            toAdd = False
        if toAdd:
            code += (l + "\n")
    return code

def replaceTabs(code):
    return code.replace("\t", "    ")

#this function is no longer needed in principle as python can define functions inside functions
def removeFunction(code):
    code = replaceTabs(code)
    newcode = ""
    deleting = False
    spacesAndTabs = ""
    oldline = ""
    for l in code.splitlines():
        if "def" in  l and "class" not in oldline: #function needed if its inside a class
            deleting = True
            spacesAndTabs = l.split('def')[0]
        elif not ( l.startswith(spacesAndTabs + " ") or l.startswith(spacesAndTabs + "\t") ):
            deleting = False
        if not deleting:
            newcode += (l + "\n")
        oldline = l
    return newcode

#remove any line from text containing a given string
def removeLine(code, string):
    newcode = ""
    for l in code.splitlines():
        if not string in l:
            newcode += (l + "\n")
    return newcode

#find x and y minima and maxima in mpoints
def findMinMax(ls): 
    extrema = [ls[0][0], ls[0][0], ls[0][1], ls[0][1]] #ymin, ymax, xmin, xmax
    for i in range(1, len(ls)):
        for j in range(0,2):
            if(ls[i][0 + j] < extrema[0 + 2*j]):
                extrema[0 + 2*j] = ls[i][0 + j]
            if (ls[i][0 + j] > extrema[1 + 2*j]):
                extrema[1 + 2*j] = ls[i][0 + j]
    return extrema
        
            

mcm = restful(dev=False)

allRequests = mcm.getA('requests',query='member_of_campaign=RunIISpring16FSPremix')
allRequests += mcm.getA('requests',query='member_of_campaign=RunIISummer16FSPremix')
samples = []
for r in allRequests:
    #if r['pwg']!='SUS' : continue
    try:
        if r['status'] != 'done':
            continue
    except:
        print r
    if "SUS" not in r['prepid']:
        continue
    #for key in r:
    #    print str(key) + ":::" + str(r[key])
    #print r['fragment']
    mpoints = []
    if goodFragment(r['fragment']):             #check if fragment defines a mass range
        #extract code initializing mass range from fragment
        temp_file = open("temp.py", "w")
        temp_file.write("import math \n")
        temp_file.write("def getMPoints(): \n")
        code = findCode(r['fragment'])
        code = removeLine(code, "import")
        code = removeLine(code, "print")
        for l in code.splitlines():
            temp_file.write("\t" + l +"\n")
        temp_file.write("\treturn mpoints")
        temp_file.close()
        execfile("temp.py")
        mpoints =  getMPoints() 
        mpoints = findMinMax(mpoints)
        samples.append( (r['dataset_name'], r['total_events'], "\thttps://cms-pdmv.cern.ch/mcm/requests?prepid=" + r['prepid'], str(mpoints[0]) + "-" + str(mpoints[1]), str(mpoints[2]) + "-" + str(mpoints[3]) )  )
    else:
        samples.append( (r['dataset_name'], r['total_events'], "\thttps://cms-pdmv.cern.ch/mcm/requests?prepid=" + r['prepid'], "", "") )



def getSortKey(item): return item[0]

samples.sort(key=getSortKey)
for el in samples:
    printString = el[0]
    for i in range(1, len(el)):
        printString += "\t" + str(el[i])
    print printString

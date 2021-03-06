'''
Grant Ikehara, Cameron Healy, Dominic Soares
HW #7
hw7.py
CPSC 310-01
Purpose:
    To implement an a priori rule miner as opposed to the decision trees
    and random forests that we've been mucking around with. We're really
    just printing out a mined ruleset and describing it.
Design Checklist:
    No steps this time, should be interesting. So here's your list:
    [] Create aPriori Algorithm. 
    For titanic Dataset:
        At various min support levels:
            [] implement algorithm, mine rules
            [] print rules
            [] describe rules, do they:
                [] make sense
                [] compare to HW4 and HW5
        [] Discuss how various min support and confidence affected this.
        
    For shroom Dataset:
        At various min support levels:
            [] implement algorithm, mine rules
            [] print rules
            [] describe rules, do they:
                [] make sense
                [] compare to HW4 and HW5
            [] Read the book so you know what feature selection is
            [] Do feature selection
        [] Discuss how various min support and confidence affected this.
        
    
Issues:
    TBD. 
'''

import csv
import sys
import math
import copy
import numpy
from tabulate import tabulate
import random
from collections import Counter

'''
The read_csv() function is the same function introduced in class. It returns a table
filled with the selected file's CSV data. It is used to open all files.
'''
def read_csv(filename):
    the_file = open(filename, 'r')
    the_reader = csv.reader(the_file, dialect='excel')
    table = []
    for row in the_reader:
        if len(row) > 0:
            table.append(row)
    the_file.close()
    return table

'''
Gets discretized mpg rating
'''
def rate(x):   #Changes ratio mpg to ordinal mpg rating. I use this often.
    4
    
    y = 0
    if x <= 13.99999:
        y = 1
    elif x >= 14.0 and x < 15:
        y = 2
    elif x >= 15.0 and x < 17.0:
        y = 3
    elif x >= 17.0 and x < 20.0:
        y = 4
    elif x >= 20.0 and x < 24.0:
        y = 5
    elif x >= 24.0 and x < 27.0:
        y = 6
    elif x >= 27.0 and x < 31.0:
        y = 7
    elif x >= 31.0 and x < 37.0:
        y = 8
    elif x >= 37.0 and x < 45.0:
        y = 9
    elif x >= 45.0:
        y = 10
    return y


'''
Discretizes weight.
'''
def rateWeight(x): #Discretizes the weight into 5 categories
    if x <= 1999.999:
        y = 1
    elif x >= 2000 and x < 2500:
        y = 2
    elif x >= 2500 and x < 3000:
        y = 3
    elif x >= 3000 and x < 3500:
        y = 4
    elif x >= 3500:
        y = 5

    return y

'''
Returns a random subset of size F from the input table 
'''
def random_attribute_subset(attributes, F):
    # shuffle and pick first F
    shuffled = attributes[:]  # make a copy
    random.shuffle(shuffled)
    return shuffled[:F]



'''
Puts autodata in a format we can deal with
'''
def rewriteTable(table): #Foregoes the whole auto-data table,
    #Instead just uses a truncated table with 4 rows, easy format.
    newTable = []
    for i in range(len(table)):
        row = []
        row.append(float(table[i][1])) #cylinders
        row.append(float(table[i][4])) #weight (discretized)
        row.append(float(table[i][6])) #modelYear
        row.append(float(table[i][0])) #mpg (discretized)
        newTable.append(row)
    i = 0
    for j in range(len(newTable)):
        newTable[j][3] = rate(newTable[j][3])
        newTable[j][1] = rateWeight(newTable[j][1])
    return newTable




'''
Gets yes/no/1-10 when we have a leaf
'''
def partStats(table, cLabel): 
    classVals = list(set(get_column(table, cLabel)))
    stats = []
    stats.append([table[0][cLabel], 1, len(table)])
    for i in range(len(table)-1):
        a = 0
        for j in range(len(stats)):
            if stats[j][0] == table[i+1][cLabel]:
                stats[j][1] += 1
                a = 1
        if a == 0:
            stats.append([table[i+1][cLabel], 1, len(table)])
    return stats #spits back of a list of lists of freqs for various labels.


'''
returns the frequencis of all attributes in the instance set as a dictionary
'''
def attribute_frequencies(instances, att_index, class_index):
    att_vals = list(set(get_column(instances, att_index))) 
    class_vals = list(set(get_column(instances, class_index)))
    result = {v: [{c: 0 for c in class_vals}, 0] for v in att_vals}
    for row in instances:
        label = row[class_index]
        att_val = row[att_index]
        result[att_val][0][label] += 1
        result[att_val][1] += 1
    return result

'''
Calculates the E_new of the instance set and returns it
'''
def calc_enew(instances, att_index, class_index):
    # get the length of the partition
    D = len(instances)
    # calculate the partition stats for att_index (see below)
    freqs = attribute_frequencies(instances, att_index, class_index)
    # find E_new from freqs (calc weighted avg)
    E_new = 0
    for att_val in freqs:
        D_j = float(freqs[att_val][1])
        probs = [(c/D_j) for (_, c) in freqs[att_val][0].items()]
        for p in range(len(probs)):
            if probs[p] == 0:
                probs[p] = 1.0
        E_D_j = -sum([p*math.log(p,2) for p in probs])
        E_new += (D_j/D)*E_D_j
    return E_new

'''
Returns the index of the attribute with the least entropy
'''
def pick_attribute(instances, att_indexes, class_index):
    ents = []
    for att_i in att_indexes:
        ents.append(calc_enew(instances, att_i, class_index))
    min_ent = ents.index(min(ents))
    return min_ent

    
'''
As self-explanatory as it gets
'''
def getRidOfFirstLine(table): #Just for the titanic
    i = 0
    newtable = []
    for row in table:
        if i != 0:
            newtable.append(table[i])
        i +=1
    return newtable


'''
Returns a random subset of size F from the input table 
'''
def random_attribute_subset(attributes, F):
    # shuffle and pick first F
    shuffled = attributes[:]  # make a copy
    random.shuffle(shuffled)
    return shuffled[:F]





'''
Checks if all labels are the same.
'''
def isSame(table, classLabel): #checks for uniformity of class label.
    isIt = 0
    original = table[0][classLabel]
    for i in range(len(table)):
        if table[i][classLabel] != original:
            isIt = 1
    return isIt


'''
Gets a column in question.
'''
def get_column(table, ind): #parse all the data into different lists
    listylist = [] #               0
    i = 0            
    for row in table: #Get nice subdivisions
        listylist.append(table[i][ind])   
        i += 1
    i = 0
    return (listylist)#return all of the lists




"""
-------------------------------------------
New functions for HW 7
-------------------------------------------
"""

"""
get_Lk(table, Lk-1):
	For each A in Lk-1 and B in Lk-1:
		If A[0:-1] == B[0:-1]:
			Add AUB to Ck unless
			aK-1 subset of AUB not in Lk-1
	Set Lk to supported itemsets in Ck
"""

def get_all_subsets(table,itemset):
    subsets = [] 
    subsets.append(k_1_subsets(itemset))
    for i in range(1, get_number_instances(table)):  #hoping break comes before end
	if(get_Lk(table,i) == []):
	    break
	else:
	    subsets.append(get_Lk(table,i))


def k_1_subsets(itemset): 
    result = [] 
    for i in range(len(itemset)): 
        result.append(itemset[:i] + itemset[i+1:] 
    return result


def get_min_support(table, percentage):
    total_instances = count_instances(table)
    number_instances_necesary = total_instances*percentage
    return number_instances_necesary


def get_support(table, attributeList, valueList):
	count = 0
	For row in table:
	    mark = 0
	    for item in row:
                if attribute in attributeList == attribute in row:
		    mark +=1
	    if mark == len(attributeList):
                count += 1
	Return count

        #Prior to executing this, do the immediately above function.

	if number of instances with given L x R > minPct:
	    return 1
	else:
	    return 0


def count_instances(table):
    """counts number of instances in table"""
    instances = 0
    for row in table:
        instances += 1
    return instances



#Moving items from LHS to RHS cant increase confidence of a role
#If no rules of RHS size k are confident, stop searching
Def breakpoint(listofrules, min_support):
    for rule in listofrules:	
        if confidence(listofrules) < min_support:
            return 0
    return 1

    
'''
The main function
'''
def main():
    table = read_csv('titanic.txt')
    
    
    print "Command is Complete"

if __name__ == '__main__':
    main()

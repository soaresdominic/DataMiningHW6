'''
Grant Ikehara, Cameron Healy, Dominic Soares
HW #6
hw6.py
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

'''
Returns the frequency of the itemset
'''
def get_itemset_freq(itemset, table):
    checks = len(itemset)
    counter = 0
    count_itemset = 0
    for row in table:
        for item in itemset:
            if item in row:
                counter += 1
        if counter == checks:
            count_itemset += 1
        counter = 0
    return count_itemset

'''
Returns the support of the itemset
'''
def get_support(itemset, table):
    count = get_itemset_freq(itemset, table)
    support = count/(len(table)*1.0)
    return support

'''
Returns the confidence of the itemset
'''
def get_confidence(itemset, table, LHS):
    count = get_itemset_freq(itemset, table)
    countL = get_itemset_freq(LHS, table)
    if countL != 0:
        conf = count/(countL*1.0)
        return conf
    else:
        return 0

'''
Returns the lift of the itemset
'''
def get_lift(itemset, table, LHS, RHS):
    supp = get_support(itemset, table)
    suppL = get_support(LHS, table)
    suppR = get_support(RHS, table)
    if suppR*suppL != 0:
        return (supp/(suppL*suppR))
    else:
        return 0

'''
Returns the list of atts by column
'''
def get_col_atts(table, cols):
    ListOfAtts = []
    for i in range(cols):
        column = get_column(table, i)
        AttsInCol = []
        for item in column:
            if item not in AttsInCol:
                AttsInCol.append(item)
        ListOfAtts.append(AttsInCol)
    return ListOfAtts



#KJASHFHJKHASKJFGHJASGFHJGAJHSGFJHKGASJKHFGJHASGFJHGASJKFGKJHAS


def RHSandLHSok(RHS, LHS, ColsOfAtts):
    for listy in ColsOfAtts:
        for val1 in RHS:
            for val2 in LHS:
                if val1 in listy and val2 in listy:
                    return False
    return True    

def get_Lk_from_Ck(Ck1, min_supp, ColsOfAtts, table):
    Ck = []
    for A in Ck1:
        for B in Ck1:
            if RHSandLHSok(A, B, ColsOfAtts) and A != B:
                if A[0:-1] == B[0:-1]:
                    Ck.append(A+B)
    Lk = []
    for item in Ck:
        if get_support(item, table) >= min_supp:
            Lk.append(item)
    return Lk

'''
A priori algorithm for titanic
'''
def apriori_titanic(table, min_supp, min_conf):
    ColsOfAtts = get_col_atts(table, 4) #Sorts attribute values by attribute
    ListOfAtts = []
    for row in table:       #Creates list of un ordered attributes
        for item in row:
            if [item] not in ListOfAtts:
                ListOfAtts.append([item])
    FinalItemset = []
    for Att in ListOfAtts:  #Adds attributes that meet min_supp to new L1
        if get_support(Att, table) >= min_supp:
            FinalItemset.append(Att)
    Lnext = FinalItemset
    while len(Lnext) != 0:  #Creates Ln lists of supportd attribute itemsets 
        Lnext = get_Lk_from_Ck(Lnext, min_supp, ColsOfAtts, table)
        for val in Lnext:
            FinalItemset.append(val)
    for item1 in FinalItemset:
        for item2 in FinalItemset:
            if set(item2) == set(item1) and item1 != item2:
                FinalItemset.remove(item1)
                break
    ListOfRules = []
    i = 1
    for LHS in FinalItemset:   #Creates list of rules from supported itemsets
        for RHS in FinalItemset:
            support = get_support(LHS+RHS, table)
            conf = get_confidence(LHS+RHS, table, LHS)
            if RHSandLHSok(LHS, RHS, ColsOfAtts) and support >= min_supp and conf >= min_conf:
                newLHS = []
                newRHS = []
                for att1 in LHS:
                    for i in range(len(ColsOfAtts)):
                        if att1 in ColsOfAtts[i]:
                            newLHS.append([att1, i])
                            break
                for att2 in RHS:
                    for j in range(len(ColsOfAtts)):
                        if att2 in ColsOfAtts[j]:
                            newRHS.append([att2, j])
                            break
                ListOfRules.append([newLHS, newRHS])
                i += 1
    for num in ListOfRules:
        print num


#AKJSFJKHKJFLSHJKLASHFJKHASJKFLHASKJLHFKLASHFJKHASKFHKJASHFKJLASHFJKLHASLKF


'''
A priori algorithm for mushrooms
'''
def apriori_mushrooms(table, min_supp, min_conf):
    ColsOfAtts = get_col_atts(table, 23)
    ListOfRules = []
    i = 1
    for group1 in ColsOfAtts:
        for att1 in group1:
            for group2 in ColsOfAtts:
                for att2 in group2:
                    support = get_support([att1, att2], table)
                    conf = get_confidence([att1, att2], table, [att1])
                    lift = get_lift([att1, att2], table, [att1], [att2])
                    if RHSandLHSok(att1, att2, ColsOfAtts) and support >= min_supp and conf >= min_conf:
                        ListOfRules.append([i, [att1], [att2], support, conf, lift])
                        i += 1
    for num in ListOfRules:
        print num


'''
The main function
'''
def main():
    print "==========================================="
    print "Titanic"
    print "==========================================="
    table0 = read_csv('titanic.txt')
    table0 = getRidOfFirstLine(table0)
    apriori_titanic(table0, 0.25, 0.75)


    print "==========================================="
    print "Agaricus lepiota"
    print "==========================================="
    table1 = read_csv('agaricus-lepiota.txt')
    #apriori_mushrooms(table1, 0.25, 0.75)


if __name__ == '__main__':
    main()
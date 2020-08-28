#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os.path
import numpy as np





def read_file(fPath,delimiter):  
    
    
    nItems = 1
    originalData  = []

    with open(fPath, 'r',buffering=10000000) as f: #open file, don't have to use pandas since list data type is used
        for line in f:
            line=line.strip() #cut \n
            line=line.strip(delimiter) #cut all commas
            tmp=line.split(delimiter)
            tmp1=[]
            for itm in tmp:
                tmp1+=[int(itm)] #change data type from string to integer
                if int(itm)>nItems: #find the largest item ID, not sure why max() fnc doesn't work properly
                    nItems=int(itm)
            originalData+=[tmp1] #add splitted line  
    
    originalData.remove(originalData[0]) #remove the column headers from original data


    return originalData,nItems




def startListRecursion(freqGraph,nItems,lst):
    
    '''
    Parameters:
        freqGraph: The data structure(eg. [ [#,[]],...] that is storing the frequency of each subset and the child nodes
        nItems:  The number of unique elements in the Dataset
        lst: The entire set [1,2,3,..] that is being analyzed
    '''
    
    
    
    size = len(lst)
    
    if size > 1 :    
        
        tle = lst[0]
        
        ref = freqGraph[tle]
        
        nextLevel(ref , nItems, 0, lst)
        
        freqGraph[ lst[0] ][0] += 1
    
    elif size == 1:
        # GETS THE ELEM OF INDEZ (lst[0]), 
        # THEN ADDS 1 TO THE FREQUENCY COUNTER
        freqGraph[ lst[0] ][0] += 1
    else:
        print('empty')
    
        
    return freqGraph



def nextLevel(lvlArray,nItems, prevLvl, lst):
    
    '''
    Parameters:
        lvlArray: an Array of form (#, []) where the first elem is the frequency counter and [] is the child array
        nItems: the number of unique elements in the Dataset
        prevLvl: The level number where this function is called 
        lst: The entire set [1,2,3,..] that is being analyzed
    '''
    
    
    curLvl = prevLvl + 1
    
    remSize = len(lst[curLvl:])
    
    
    if remSize > 1 :
        
        
        if len(lvlArray[1]) == 0:
        
            newLvl = [ [0,[]] for i in range( lst[curLvl], nItems  ) ]
            lvlArray[1] = newLvl 
            
        
        # THIS LEVEL'S ELEMENT INDEX
        tleIx =  (lst[curLvl] - lst[prevLvl] ) - 1

        ref = lvlArray[1][tleIx] 
    
        nextLevel( ref ,nItems, curLvl, lst)
          
    
    
    lvlArray[0] += 1
    
    


def main(fPath, delimiter, minSuppRate):
    
    '''
    Parameters:
        fName: File name of the dataset
        delimiter: what is used to seperate the data in the file
        minSuppRate: minimum support rate of accepted frequencies
       
    '''
    
    # STORES A LIST OF 'SETS'
    # EACH ELEMENT IS A TRANSACTION WITH SOME 'LIST'
    # nItems: number of unique elements in the dataset
    DATASET,nItems = read_file(fPath,delimiter)
    


    ##### CREATE FREQUENCY GRAPH DATA STRUCTURE #####
    
    # CREATE A LIST OF LISTS, WERE THE FIRST ELEMENET CONTAINS THE FREQUENCY
    # AND THE SECOND ELEMENT CONTAINS THE NEXT LEVEL
    lvl0 = [ [0,[]] for i in range( nItems +1 ) ]
    
    freqGraph = lvl0

    for lst in DATASET:
        
         freqGraph = startListRecursion(freqGraph, nItems , lst)
        
        
    ### READ THE FREQUENCY GRAPH TO COLLECT THE SUBSETS THAT PASS THE 'minSuppRate' ###
         
    
    ### TO BE CONTINUED




if __name__ == '__main__':
    
    directory = './data/'
    filename = 'smallSet.csv'
    file_path = os.path.join(directory, filename)
    
    
    delimiter="," 
    minSuppRate=0.025 
    
    main(file_path,delimiter,minSuppRate)
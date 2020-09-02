#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os.path
import numpy as np
from scipy.special import comb as nCr




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
    
    ########################
    ###  INITIALIZATION  ###
    ########################
    
    # SINGLE ITEM FREQUENCY ARRAY [0,1,2,......,]
    # EACH INDEX IS AN 'ITEM'
    sif = np.zeros(nItems+1)    
    
    # NUMBER OF TRANSACTIONS        
    nTrans = len(DATASET)  
    
    # MINIMUM SUPPORT ( RATE * # OF TRANSACTIONS)
    minSupp = int(round(minSuppRate*nTrans,0))
    

    # ADD 1 TO THE ITEM IF IT'S IN THE TRANSACTION
    for trn in DATASET:
        sif[trn]+=1    
    
    logicalIx = sif > minSupp
    
    # STORE THE 'ITEMS' THAT HAD A FREQUENCY > 'minSupp'
    # fi: FREQUENT ITEMS
    fi = np.where( logicalIx == 1)[0]
    
    # NUMBER OF 'fi'
    nfi = len(fi)
    
    # ffi: FREQUENCY OF FREQUENT ITEMS
    ffi = sif[fi]
    
    # INDECES OF THE SORTED 'ffi' IN ASCENDING ORDER
    idxSort = np.argsort(ffi)[::-1]
    
    
    # AT THE MOMENT, THIS WILL ONLY WORK FOR 'fi' GREATER THAN 3
    
    # CREATE AN nCr(nfi,3) ARRAY 
    sub3 = [[] for i in range(int(nCr(nfi,3)))]
    
    # CREATE AN nCr(nfi,2) ARRAY
    sub2 = np.zeros(int(nCr(nfi,2)))
    
    
    # CREATE A HASHKEY TO MAP ITEMSETS TO APPROPIATE SUBSETS
    hashkey = np.zeros((nfi-1,2))
    
    for ii in range(nfi-1):
        for kk in [1,2]:
            
            hashkey[ii,kk-1] = nCr(ii,kk)
    
    print(hashkey)

    ######################
    ###  COMPUTATIONS  ###
    ######################
    
    
    
    # for trn in DATASET:
        
    #     c = trn[logicalIx]
    #     cl = len(c)
        
        
        
        
    








if __name__ == '__main__':
    
    directory = './data/'
    filename = 'nTrn50_nItems7.csv'
    file_path = os.path.join(directory, filename)
    
    
    delimiter="," 
    minSuppRate= 0.3
    
    main(file_path,delimiter,minSuppRate)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os.path
import numpy as np
from scipy.special import comb as nCr




def read_file(fPath,delimiter):  
    
    '''
    Parameters:
        fPath: The path in which the file is located. Can be a full/relative path
        delimiter: The character that is seperating the data items
    '''
    
    
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

   



def main(fPath, delimiter, minSupp):
    
    '''
    Parameters:
        fName: File name of the dataset
        delimiter: what is used to seperate the data in the file
        minSuppRate: minimum support rate of accepted frequencies
        minSupp: minimum support frequency of accepted items
       
    '''
    
    # STORES A LIST OF 'SETS'
    # EACH ELEMENT IS A TRANSACTION WITH SOME 'LIST'
    # nItems: number of unique elements in the dataset
    DATASET,nItems = read_file(fPath,delimiter)
    
    ########################
    ###  INITIALIZATION  ###
    ########################
    
  
    
    # I'LL UNCOMMENT THIS LATER
    ################################
    # NUMBER OF TRANSACTIONS        
    #nTrans = len(DATASET)  
    
    # MINIMUM SUPPORT ( RATE * # OF TRANSACTIONS)
    #minSupp = int(round(minSuppRate*nTrans,0))
    ################################
    print('minSupp: ',minSupp)
    
    
    
    # SINGLE ITEM FREQUENCY ARRAY [0,1,2,......,]
    # EACH INDEX IS AN 'ITEM'
    sif = np.zeros(nItems+1)      
    
    

    # ADD 1 TO THE ITEM IF IT'S IN THE TRANSACTION
    for trn in DATASET:
        sif[trn]+=1    
    
    # LOGICAL ARRAY WHERE 1 IF ITEM'S FREQ. IS >= TO THE ACCEPTED FREQ. ELSE 0
    logicalIx = sif > minSupp
    
    # STORE THE 'ITEMS' THAT HAD A FREQUENCY > 'minSupp'
    # fi: FREQUENT ITEMS
    fi = np.where( logicalIx )[0].astype(int)
    
    # NUMBER OF 'fi'
    nfi = len(fi)
    
    # ffi: FREQUENCY OF FREQUENT ITEMS
    ffi = sif[fi]
    
    # INDECES OF THE SORTED 'ffi' IN ASCENDING ORDER
    idxSort = np.argsort(ffi)  #(0: less freq )
    
    # sfi: SORTED FREQ. ITEMS
    # SORTED THE FREQ. ITEMS FROM SMALLEST FREQ. TO LARGEST FREQ.
    sfi = fi[idxSort]
    
    # WILL BE USED IN PLACE OF THE 'fi' FOR THE ALGORITHM
    # INDEX 0 INDICATES THE SMALLEST FREQ. ITEM
    proxyIID = np.arange(0,nfi)    
    
    # WILL BE USED TO SELECT THE ITEMS PER TRANSACTION
    indicator = np.zeros(nItems+1,dtype=bool)
    
    # DATA STRUCTURE USED TO STORE THE FREQ. COUNT FOR 2 ITEMS AS WELL AS STORE TRANSACTION ID
    # THE UPPER TRIANGLE WILL STORE THE FREQ COUNT
    # THE LOWER TRIANGLE WILL STORE THE TRANSACTION ID
    NL = np.zeros( (nfi,nfi ), dtype = int).tolist()
    
    # DATA STRUCTURE USED TO STORE THE L' FOR 2 ITEMS AS WELL AS L"
    # THE UPPER TRIANGLE WILL STORE L'
    # THE LOWER TRIANGLE WILL STORE L"  
    LpLpp = np.zeros( (nfi,nfi ), dtype = int).tolist()
    
    

    freq_marker = []
    
    # NOTE: IN THE LOOP, THE ALGO. WILL IGNORE THE ITEMSETS 
    # THAT DO NOT HAVE THE FREQ. ITEMS. THE TID FOR THESE ITEMSETS WILL NOT BE RECORDED.
    # IN THE PROCESS, THE ITEMSET THAT DO HAVE THE FREQ. ITEMS WILL BE REWRITTEN USING THE PROXY ID.
    # THE PROXY ITEMSET WILL BE STORED IN THE TID.
    for TID,itemset in enumerate(DATASET):
        
        # GET FREQUENT ITEMS FROM CURRENT ITEMSET
        # FREQUENT ITEMS ARE SORTED BASED ON THE 'sfi'
        indicator[itemset] = 1
        logicalArray =  indicator[sfi]
        curItemset = proxyIID[logicalArray]
        
        # STORE THE FREQ. COUNT FOR 2-ITEMSET (a,b)
        if len(curItemset) == 2:
            a,b = curItemset
            NL[a][b] += 1
            
        # TRUNCATE THE CURRENT ITEMSET 
        # STORE THE TID FOR LATER
        elif len(curItemset) > 2:
            
            a,b = curItemset[:2]
            DATASET[TID] = curItemset[2:]
                   
            if isinstance(NL[b][a],int):
                NL[b][a] = []
            
            NL[b][a].append(TID)
        
        # CLEAR THE INDICATOR FOR REUSE
        indicator[itemset] = 0   
        
            	

    # GET A LIST OF LENGTHS FROM LIST OF LIST
    funcLenLst = lambda x: list(map( len , x))
    # GET THE SUM OF THE LENGTHS OF A LIST OF LIST
    sumLen = lambda x: sum(funcLenLst(x))
    
    # a < b in terms of frequency
    # a != b
    for a in range(nfi):
        for b in range(a+1,nfi):
            
            Done = False
            
            while(not(Done)):
                
                # DEFINE THE LIST IF NOT PRESENT
                if isinstance(NL[b][a],int):
                    NL[b][a] = []
                if isinstance(LpLpp[a][b],int):
                    LpLpp[a][b] = []
                if isinstance(LpLpp[b][a],int):
                    LpLpp[b][a] = []
                
                
                print('{}: {}  {}  {}  {}'.format((a,b),NL[a][b], len( NL[b][a] ), len(LpLpp[a][b]), len(LpLpp[b][a])))
                print('{}: {}  {}  {}  {}'.format( (a,b),NL[a][b], len( NL[b][a] ), sumLen( LpLpp[a][a+1:b+1] ), sumLen( [x[a] for x in LpLpp[a+1:b+1]] ) ) )
                print('')
                
                # N_a_b + |L_a_b| + |L'_a_b| + |L"_a_b|
                if NL[a][b] + len( NL[b][a] ) + len(LpLpp[a][b]) + len(LpLpp[b][a]) >= minSupp:
                    
                    Done = True
                    freq_marker.append([a,b])
                    
                # N_a_b       + |L_a_b|         + (  |L'_a_{a+1}| + ... + |L'_a_{b-1}| + |L'_a_b|) + ( |L''_a_{a+1}|+ ... + |L"_a_{b-1}| + |L''_a_b| )
                elif NL[a][b] + len( NL[b][a] ) + sumLen(LpLpp[a][a+1:b+1])  +  sumLen([x[a] for x in LpLpp[a+1:b+1]])  <  minSupp:
                    
                    
                    Done = True
                
                # THIS SECTION IS STILL A WORK IN PROGRESS
                else:
                    print('other')
                    
                    # FIND c'
                    cp = a + 1 + np.argmax( funcLenLst( LpLpp[a][a+1:b+1] ) )
                    
                    # Find c"
                    cpp = a + 1 + np.argmax( funcLenLst( [ x[a] for x in LpLpp[a+1:b+1] ] ) )
                    
                    # GET L_a_c'
                    lp_ac = LpLpp[a][cp]
                    
                    # GET L_a_c"
                    lpp_ac = LpLpp[cpp][a]
                    
                    # |L_a_c'| < |L_a_c"|
                    if len(lp_ac) < len(lpp_ac):
                        
                        for pointer,tid  in lpp_ac:
                            
                            curItem = DATASET[tid]
                            
                            
                            if isinstance(LpLpp[curItem[pointer]][b],int):
                                LpLpp[curItem[pointer]][b] = []
                            

                            LpLpp[curItem[pointer]][b].append([pointer+1,tid])  
                            
                        # zero out after redistribution ?
                        LpLpp[cpp][a] = []  
                        
                    else:
                        
                        
                        for tid  in lp_ac:
                        
                            curItem = DATASET[tid]
                            
                            if isinstance(LpLpp[b][cp],int):
                                LpLpp[b][cp] = []
                            
                            LpLpp[b][cp].append(tid)   

                        # zero out after redistribution ?
                        LpLpp[a][cp] = []
                                          
                                                   
		

            # redistribute
            idx_for_del = []
            for idx,tid in enumerate(NL[b][a]):
                
                curItem = DATASET[tid]
                c = curItem[0]
                
                # ITEMSET ONLY HAS ONE ITEM LEFT STORED
                # REDISTRIBUTE THIS ITEMSET TO THE FREQ. COUNT
                if len(curItem) == 1:
                    
                    NL[a][b] +=1
                    NL[a][c] +=1
                    NL[b][c] +=1
                    
                    # RECORD WHAT INDEX WILL BE DELETED
                    idx_for_del.append(idx)
                else:
                    
                    # DEFINE IN THE LIST IF NOT PRESENT
                    if isinstance(NL[c][b] , int ):
                        NL[c][b] = [] # L_b_c
                    if isinstance ( LpLpp[a][c] , int):
                        LpLpp[a][c] = [] # L'_a_c
                    
                    
                    # STORE TID IN L_#_b
                    NL[c][b].append(tid)
                    
                    # STORE L'_a_#
                    LpLpp[a][c].append(tid)
                    
                    # POP THE FIRST ELEMENT OFF. NO LONGER IN USE.
                    DATASET[tid] = DATASET[tid][1:]
                    
            # L_a_b DELETE TID THAT NO LONGER RELEVENT 
            NL[b][a] = np.delete(NL[b][a], idx_for_del)     


    print('')
    print('Freq 2-Itemsets')
    for a,b in freq_marker:
        
        #print( (sfi[a],sfi[b]), ':',NL[a][b])
        #print( (a,b), ':',NL[a][b])
        print('Proxy:({},{}) Actual:({},{})'.format(a,b,sfi[a],sfi[b]))
            






























if __name__ == '__main__':
    
    directory = './data/'
    filename = 'nTrn50_nItems7.csv'
    file_path = os.path.join(directory, filename)
    
    
    delimiter="," 
    minSuppRate= 8
    
    main(file_path,delimiter,minSuppRate)
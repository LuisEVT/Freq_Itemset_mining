#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os.path
import numpy as np
from scipy.special import comb as nCr
import time




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

   



def main(fPath, delimiter, minSuppRate):
    
    '''
    Parameters:
        fName: File name of the dataset
        delimiter: what is used to seperate the data in the file
        minSuppRate: minimum support rate of accepted frequencies
        minSupp: minimum support frequency of accepted items
       
    '''
    t1=time.perf_counter()
    # STORES A LIST OF 'SETS'
    # EACH ELEMENT IS A TRANSACTION WITH SOME 'LIST'
    # nItems: number of unique elements in the dataset
    DATASET,nItems = read_file(fPath,delimiter)
    
    t2=time.perf_counter()
    
    ########################
    ###  INITIALIZATION  ###
    ########################
    
  
    
    # I'LL UNCOMMENT THIS LATER
    ################################
    # NUMBER OF TRANSACTIONS        
    nTrans = len(DATASET)  
    
    # MINIMUM SUPPORT ( RATE * # OF TRANSACTIONS)
    minSupp = int(round(minSuppRate*nTrans,0))
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
    
    #print('sff:{}'.format(ffi[idxSort]))
    print('sfi:{}'.format(sfi))
    print('pro:{}'.format(proxyIID))
    
    
    
    
    generate_lst = lambda N: [ [0,[],[],[]] for i in range(N) ]
    
    struc2D = [generate_lst(n) for n in range(nfi,0,-1)]
    
    
    
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
            
            # ADD 1 TO THE FREQ. OF (a,b)-ITEMSET
            struc2D[a][b-(a+1)][0] += 1
            

            
        # TRUNCATE THE CURRENT ITEMSET 
        # STORE THE TID FOR LATER
        elif len(curItemset) > 2:
            
            # GET THE FIRST TWO ELEM FOR INDEXING
            a,b = curItemset[:2]
            
            # TRUNCATE THE FIRST TWO ITEMS
            DATASET[TID] = curItemset[2:]
                   
            # INDEX THE TID INTO THE DATA STRUCTURE
            # RECALL THAT B MUST BE SHIFTED BY (a+1)
            struc2D[a][b-(a+1)][1].append(TID)
        
        # CLEAR THE INDICATOR FOR REUSE
        indicator[itemset] = 0       
    
    
    # KEEP TRACK OF FREQ. 2-ITEMSETS
    # WILL STORE ELEM AS SUCH: [a,b,#]
    # WHERE a,b ARE THE PROXY ELEMS AND # IS THE FREQ.
    freq_marker = []
    
    
    
  
    
    # a < b in terms of frequency
    for a in range(nfi):
        for b in range(nfi - (a+1)): # PROXY VALUE SHIFT BY (a+1) 
        
            # STATE IF FREQ. OF (a,b)-ITEMSET HAS BEEN DETERMINED
            Done = False
            
            while(not(Done)):
                
                
                #print("\n({},{}): N:{}  L:{}  Lp:{}  Lpp:{}".format(a,b,struc2D[a][b][0],len(struc2D[a][b][1]),len(struc2D[a][b][2]),len(struc2D[a][b][3])))
                
                # N_a_b + |L_a_b| + |L'_a_b| + |L"_a_b|
                minThreshold = struc2D[a][b][0] + len(struc2D[a][b][1]) + len(struc2D[a][b][2]) + len(struc2D[a][b][3])
                
                ################
                ## CONDITION 1
                ################
                
                # CHECK IF FREQ. IS GREATER THAN THE MIN SUPPORT
                if minThreshold >= minSupp:

                    Done = True
                    # MARK (a,b)-ITEMSET AS FREQ.
                    freq_marker.append([a,b,minThreshold])
                    continue 
                
                ################
                ## CONDITION 2
                ################                
                
                #print("({},{}): N:{}  L:{}  Lp:{}  Lpp:{}".format(sfi[a],sfi[b+(a+1)],struc2D[a][b][0],len(struc2D[a][b][1]),sum([len(struc2D[a][i][2]) for i in range(b+1)]),sum([len(struc2D[a][i][3]) for i in range(b+1)])))

                # N_a_b  + |L_a_b| + (  |L'_a_0| + ... + |L'_a_b|) + ( |L''_a_0|+ ...  + |L''_a_b| )
                predThreshold = struc2D[a][b][0] + len(struc2D[a][b][1]) + sum([len(struc2D[a][i][2]) for i in range(b+1)]) + sum([len(struc2D[a][i][3]) for i in range(b+1)])
        
                # CHECK IF FREQ. IS LESS THAN THE MIN SUPPORT
                # IF SO, THEN FREQ. FOR THIS (a,b)-ITEMSET WONT MEET THE REQ.
                if predThreshold < minSupp:
                    Done = True
                    continue


                ################
                ## CONDITION 3
                ################

                # FIND c' and c" SUCH WHERE max(|L_a_c|) , WHERE max(|L"_a_c|) and c < b
                cp = np.argmax(  [len(struc2D[a][i][2]) for i in range(b)]  )
                cpp = np.argmax( [len(struc2D[a][i][3]) for i in range(b)]  )
    

                # | L'_ac| < |L"_ac|
                if len(struc2D[a][cp][2]) <= len(struc2D[a][cpp][3]):

                    # REDISTRIBUTE L"_ac" to L"_bc
    

                    # ITERATE THROUGH THE ELEMS STORED IN L"_ac"
                    for pointer,TID in struc2D[a][cpp][3]:
                        
                        curItem = DATASET[TID]
                        
                        # MAKE SURE THAT THE ITEMSET HAS ANOTHER ELEM TO POINT
                        if len(curItem) > pointer+1 :
                            
                            # L"_ac" to L"_ac , where c is the next elem
                            c =  curItem[pointer+1]
                            proxC = c - (a+1)
                            struc2D[a][proxC][3].append( [pointer+1 , TID] ) 
                            
                            
                    # EMPTY OUT L"_ac"
                    struc2D[a][cpp][3] = []
    
      
                else:
                    
                    # REDISTRIBUTE L'_ac' to L"_bc
                    
                    # ITERATE THROUGH THE ELEMS STORED IN L'_ac'
                    for TID in struc2D[a][cp][2]:
    
                        curItem = DATASET[TID]   
                        
                        # L'_ac' to L"_ac, where c is the next elem
                        c = curItem[0]
                        proxC = c - (a+1)
                        
                        if len(curItem) == 1:
                            
                            struc2D[a][proxC][0] += 1                            
                        
                        else:

                            struc2D[a][proxC][3].append([0,TID])
                        
                      
                    # EMPTY OUT L'a_c'
                    struc2D[a][cp][2] = []
             
                    
             
            
            # REDISTRIBUTE L_ab to L'ac and also to L_bc
            # ITERATE THROUGH THE ELEMS STORED IN L_ab
            for tid in struc2D[a][b][1]:
                
                curItem = DATASET[tid]
                c = curItem[0]
                
                # ITEMSET ONLY HAS ONE ITEM LEFT STORED
                # REDISTRIBUTE THIS ITEMSET TO THE FREQ. COUNT
                if len(curItem) == 1:
                    
                    proxB = b + (a+1)
                    proxC = c - (proxB+1)
                    
                    
                    struc2D[a][c-(a+1)][0] += 1
                    struc2D[proxB][proxC][0] += 1
                    
                    
                else:
                    
                    proxB = b + (a+1)
                    proxC = c - (proxB+1)
                    
                    # STORE TID IN L_#_b
                    struc2D[proxB][proxC][1].append(tid)
 
                    
                    # STORE L'_a_#
                    struc2D[a][c-(a+1)][2].append(tid)

                    
                    # POP THE FIRST ELEMENT OFF. NO LONGER IN USE.
                    DATASET[tid] = DATASET[tid][1:]
                
                
            # EMPTY OUT L_ab
            struc2D[a][b][1] = []

        # CLEAR ALL OF N_a# , L_a# , L'_a#, L"_a#
        struc2D[a] = 0 




    t3=time.perf_counter()
    
    print('\nData reading time:',t2-t1) 
    print('Mining time:      ',t3-t2)
    print('Total time:       ',t3-t1)

    print('')
    print('Itemset: Min Freq.')
    print('-----------------------------')
    
    for a,b,freq in freq_marker:
        
        #print('Proxy:({},{}) Actual:({},{}) minFreq: {}'.format(a,b+(a+1),sfi[a],sfi[b+(a+1)],freq))
        print('({},{}): {}'.format(sfi[a],sfi[b+(a+1)],freq))
            
    print('-----------------------------')



    









if __name__ == '__main__':
    
    directory = './data/'
    
    ### MY DATASET
    # filename = 'nTrn50_nItems7.csv'
    # file_path = os.path.join(directory, filename)
    # delimiter="," 
    # minSuppRate= 0.15
    
    # ### KOSARAK DATASET
    filename = 'kosarak.dat'
    file_path = os.path.join(directory, filename)
    delimiter=" "   
    minSuppRate = 0.025
    
    
    
    
    
    main(file_path,delimiter,minSuppRate)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
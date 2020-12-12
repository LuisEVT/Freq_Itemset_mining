
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
                
                item = int(itm) # change data type from string to integer
                
                tmp1.append(item) 
                
                if item > nItems: 
                    nItems= item
                    
            originalData+=[tmp1] #add splitted line  
    
    originalData.remove(originalData[0]) #remove the column headers from original data


    return originalData,nItems


def recFunction( recStruc, prefix , minSupp , nfi, dataset ): 
    
    '''
    Parameters:
        recStruc: a list of list that contains the N_abc and L_abc
        prefix: A list that contains the proxy items [a,b,..] that where freq.
        minSupp: minimum support of accepted frequencies
        nfi: Number of single freq. items
        dataset: list that contains the itemsets based on TID
    '''
    
    freq_marker = []

    # GET THE PREV SHIFT
    prevShift =  prefix[-1] + 1
    
    for c in range(len(recStruc)):
        
        
        # N_..c + L_..c
        minThreshold = recStruc[c][0] + len(recStruc[c][1]) 


        # GET THE UNSHIFTED PROXY VALUE OF C
        proxC = c + prevShift
        
        # CHECK IF THE ITEMSET (a,b,c,..) is freq.
        if minThreshold >= minSupp :
            

            
            # ADD THIS FREQ. ITEMSET TO THE LIST
            freq_marker.append([prefix+[proxC], minThreshold])
        
            # CREATE A NEW recStruc DATA STRUCTURE FOR THE NEXT ITERATION
            recStruc2 = [ [0,[]] for i in range(nfi - (proxC+1)) ]
            
            
            # DISTRIBUTE L_..c to L_..cd
            for pointer,TID in recStruc[c][1]:
            
                # GET THE ITEMSET CORRESPONDING TO THIS TID
                curItem  = dataset[TID]
                
                # CHECK THAT ITEMSET CAN EXPAND TO L_..ad
                # IT IT ONLY HAD L_..ad, then count it as a freq.
                if len(curItem) == pointer + 2 :
                    
                    d = curItem[pointer+1]
                              
                    # N_d
                    proxD = d - prevShift
                    recStruc[proxD][0] += 1
                    

                    #N_cd
                    proxD = d - (proxC+1) 
                    recStruc2[proxD][0] += 1
                    
                    
                    
                # CHECK THAT ITEMSET CAN EXPAND TO L_..ad
                # IF IT CAN EXPAND BEYOND L_..ad, THEN STORE IN :L_..cd                 
                else:   
                   
                   # L_c -> L_cd
                   d = curItem[pointer+1]
                   
                   proxD = d - (proxC+1) 
                   recStruc2[proxD][1].append([pointer+1,TID])                 
                   
                   
                   # REDISTRIBUTE L_..c -> L_..d 
                   # MAKE SURE THAT THE ITEMSET HAS ANOTHER ELEM TO POINT 
                   
                   proxD = d - prevShift
                   recStruc[proxD][1].append([pointer+1,TID])      
                   
            # CLEAR L_..c
            recStruc[c][1] = []  
            
            
            
            
               
            # RECURSE L_..cd
            mark = recFunction( recStruc2, prefix+[proxC] , minSupp , nfi, dataset )
            
            # ADD THE FREQ. ITEMSETS FROM THE RECURSION TO THE LIST
            freq_marker.extend(mark)
            
         
        else:     
            
            # REDISTRIBUTE L_..c -> L_..d
            for pointer,TID in recStruc[c][1]:
                
                # GET THE ITEMSET CORRESPONDING TO THIS TID
                curItem  = dataset[TID]              
                d = curItem[pointer+1]
                proxD = d - prevShift
                
                # MAKE SURE THAT THE ITEMSET HAS ANOTHER ELEM TO POINT
                if len(curItem) == pointer + 2 :
                    
                    recStruc[proxD][0] += 1                    

                else:   

                   recStruc[proxD][1].append([pointer+1,TID])      
                   
            # CLEAR L_..c
            recStruc[c][1] = []
                
                
    return freq_marker
                

def main(fPath, delimiter, minSuppRate):
    '''
    Parameters:
        fName: File name of the dataset
        delimiter: what is used to seperate the data in the file
        minSuppRate: minimum support rate of accepted frequencies
       
    '''
    
    # Timers
    readTime = 0.0
    mineTime = 0.0
    
    
    
    
    t1=time.perf_counter()
    
    # STORES A LIST OF 'SETS'
    # EACH ELEMENT IS A TRANSACTION WITH SOME 'LIST'
    # nItems: number of unique elements in the dataset
    DATASET,nItems = read_file(fPath,delimiter)
    
    t2=time.perf_counter()
    
    readTime = t2 - t1
    
    ########################
    ###  INITIALIZATION  ###
    ########################
    

    ################################
    # NUMBER OF TRANSACTIONS        
    nTrans = len(DATASET)  
    
    # MINIMUM SUPPORT ( RATE * # OF TRANSACTIONS)
    minSupp = int(round(minSuppRate*nTrans,0))
    
    ################################
    
    
    
    # SINGLE ITEM FREQUENCY ARRAY [0,1,2,......,]
    # EACH INDEX IS AN 'ITEM'
    sif = np.zeros(nItems+1).astype(int)      
    
    # count = 0

    # ADD 1 TO THE ITEM IF IT'S IN THE TRANSACTION
    for trn in DATASET:
        sif[trn]+=1    
    
    # LOGICAL ARRAY WHERE 1 IF ITEM'S FREQ. IS >= TO THE ACCEPTED FREQ. ELSE 0
    logicalIx = sif >= minSupp
    
    # STORE THE 'ITEMS' THAT HAD A FREQUENCY > 'minSupp'
    # fi: FREQUENT ITEMS
    fi = np.where( logicalIx )[0].astype(int)
    
    # NUMBER OF 'fi'
    nfi = len(fi)

    # ffi: FREQUENCY OF FREQUENT ITEMS
    ffi = sif[fi]
    
    
    # ALGORITHM REALLY ONLY WORKS IF THERE'S MORE THAN TWO FREQ SINGLE ITEMS.
    if nfi == 0 :
        return minSupp, readTime, 0.0 ,nfi, []
    elif nfi == 1:
        return minSupp, readTime, 0.0 ,nfi, [[fi.tolist(),ffi.tolist()[0]]] 
    
    
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
    #print('sfi:{}'.format(sfi))
    #print('pro:{}'.format(proxyIID))
    
    
    
    # LAYER B HAS: [ N_ab, L_ab, L'_ab , L"_ab ] on every b in a
    generate_lst = lambda N: [ [0,[],[],[]] for i in range(N) ]

    struc2D = [generate_lst(n) for n in range(nfi,0,-1)]
    
    

    # NOTE: IN THE LOOP, THE ALGO. WILL IGNORE THE ITEMSETS 
    # THAT DO NOT HAVE THE FREQ.  SINGLE ITEMS. THE TID FOR THESE ITEMSETS WILL NOT BE RECORDED.
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
        
        shiftA = a + 1
        
        for b in range(nfi - shiftA): # PROXY VALUE SHIFT BY (a+1) 
            #print('({},{})'.format(a,b))
            proxyB = b + shiftA
        
            # STATE IF FREQ. OF (a,b)-ITEMSET HAS BEEN DETERMINED
            notDone = True
            isFreq = False
            while(notDone):
                
                # N_a_b + |L_a_b| + |L'_a_b| + |L"_a_b|
                minThreshold = struc2D[a][b][0] + len(struc2D[a][b][1]) + len(struc2D[a][b][2]) + len(struc2D[a][b][3])
                
                ################
                ## CONDITION 1
                ################
                
                #print('({},{}):{}'.format(a,b,minThreshold))
                
                # CHECK IF FREQ. IS GREATER THAN THE MIN SUPPORT
                if minThreshold >= minSupp:
                    isFreq = True
                    notDone = False
                    # MARK (a,b)-ITEMSET AS FREQ.
                    freq_marker.append([[a,proxyB],minThreshold])
                    continue 
                
                ################
                ## CONDITION 2
                ################                
                
                # list of length for L'_ai , where i <= b
                Lp_len = [len(struc2D[a][i][2]) for i in range(b+1)]
                
                # list of length for L"_ai , where i <= b
                Lpp_len = [len(struc2D[a][i][3]) for i in range(b+1)]
                

                # N_a_b  + |L_a_b| + (  |L'_a_0| + ... + |L'_a_b|) + ( |L''_a_0|+ ...  + |L''_a_b| )
                predThreshold = struc2D[a][b][0] + len(struc2D[a][b][1]) + np.sum(Lp_len) + np.sum(Lpp_len)
                
                #print('({},{}):{}'.format(a,b,predThreshold))
                #print('')
        
                # CHECK IF FREQ. IS LESS THAN THE MIN SUPPORT
                # IF SO, THEN FREQ. FOR THIS (a,b)-ITEMSET WONT MEET THE REQ.
                if predThreshold < minSupp:
                    notDone = False
                    continue


                ################
                ## CONDITION 3
                ################

                # FIND c' and c" SUCH WHERE max(|L_a_c|) , WHERE max(|L"_a_c|) and c < b
                cp = np.argmax(  Lp_len[:-1] )
                cpp = np.argmax( Lpp_len[:-1] )
    

                # | L'_ac| < |L"_ac|
                #if len(struc2D[a][cp][2]) <= len(struc2D[a][cpp][3]): # improved 
                if Lp_len[cp] <= Lpp_len[cpp]:

                    # REDISTRIBUTE L"_ac" to L"_bc
    

                    # ITERATE THROUGH THE ELEMS STORED IN L"_ac"
                    for pointer,TID in struc2D[a][cpp][3]:
                        
                        curItem = DATASET[TID]  
                        
                        c =  curItem[pointer+1]
                        proxC = c - shiftA
                        
                        # MAKE SURE THAT THE ITEMSET HAS ANOTHER ELEM TO POINT
                        if len(curItem) == pointer+2 :
                            
                            struc2D[a][proxC][0] += 1
                            
                            
                        else:
                            
                            # L"_ac" to L"_ac , where c is the next elem

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
                        proxC = c - shiftA
                        
                        if len(curItem) == 1:
                            
                            struc2D[a][proxC][0] += 1                            
                        
                        else:

                            struc2D[a][proxC][3].append([0,TID])
                        
                      
                    # EMPTY OUT L'a_c'
                    struc2D[a][cp][2] = []
             
             
             
            
            # WAS (a,b) FREQ. ?
            if isFreq:
                
                ######################
                # UNBOX ALL L' AND L''   
                ######################
                
                # L'_ai and L''_ai WHERE i < b
                for i in range(b):
                    
                    
                    # ITERATE THROUGH THE ELEMS STORED IN L'_ai'
                    for TID in struc2D[a][i][2]:
    
                        curItem = DATASET[TID]   
                        
                        # L'_ai to L"_ac, where c is the next elem
                        c = curItem[0]
                        proxC = c - shiftA
                        
                        if len(curItem) == 1:
                            struc2D[a][proxC][0] += 1                            
                        else:
                            struc2D[a][proxC][3].append([0,TID])
                        
                      
                    # EMPTY OUT L'a_i
                    struc2D[a][i][2] = []                      
                    
                    
                    
                    # ITERATE THROUGH THE ELEMS STORED IN L"_ai
                    for pointer,TID in struc2D[a][i][3]:
                        
                        curItem = DATASET[TID]
                        
                        c =  curItem[pointer+1]
                        proxC = c - shiftA
                        
                        # MAKE SURE THAT THE ITEMSET HAS ANOTHER ELEM TO POINT
                        if len(curItem) == pointer+2 :
                            
                            struc2D[a][proxC][0]+=1 
 
                        else:
                            # L"_ai to L"_ac , where c is the next elem

                            struc2D[a][proxC][3].append( [pointer+1 , TID] )                                                     
                            
                            
                            
                    # EMPTY OUT L"_ai
                    struc2D[a][i][3] = []
                            
                  
                        
                
                #################
                # CONSTRUCT L_abc
                #################
                
                
                # CREATE THE DATA STRUCTURE FOR THE RECURSION
                recStruc = [ [0,[]] for i in range(nfi - (proxyB+1)) ]
                
                # L_ab -> L_abc
                for TID in struc2D[a][b][1]:
                    
                    # ALL ITEMSETS WILL HAVE ATLEAST ONE ITEM
                    curItem = DATASET[TID]
                    
                    c = curItem[0]
                    # ALL VALUES OF C MUST BE SHIFTED BY (B+1)
                    proxC = c - (proxyB+1)
                    
                    
                    if len(curItem) == 1:
                        
                        # L_ab -> N_abc
                        recStruc[proxC][0]+=1
                        
                        
                        # ITEMSET ONLY HAS ONE ITEM LEFT STORED
                        # REDISTRIBUTE THIS ITEMSET TO THE FREQ. COUNT
                        
                        # L_ab -> N_bc
                        struc2D[a][c-shiftA][0] += 1
                        
    
                        struc2D[proxyB][proxC][0] += 1                        
                        

                    else:
                        # L_ab -> L_abc
                        # REASON FOR -1: WE'RE ABOUT TO POP OFF [c] FROM THE ITEMSET
                        # SO, THE POINTER WILL HAVE TO START AT -1
                        # IN THE RECURSION, IT'LL ADD 1 AND START AT 0, WHICH IS [d]
                        recStruc[proxC][1].append([-1,TID])
                        
                        
                        # L_ab -> L_bc & L'_ac
                        
                        ## THIS SECTION IS FOR REDISTRIBUTING L_ab
                        
                        # STORE TID IN L_bc
                        struc2D[proxyB][proxC][1].append(TID)
         
                        
                        # STORE L'_ac
                        struc2D[a][c-shiftA][2].append(TID)
        
                        
                        # POP THE FIRST ELEMENT OFF. NO LONGER IN USE.
                        DATASET[TID] = DATASET[TID][1:]                        
                        

                        
                    
                # L'_ab -> L_abc
                for TID in struc2D[a][b][2]:
                    
                    # ALL ITEMSETS WILL HAVE ATLEAST ONE ITEM
                    curItem = DATASET[TID]
                    
                    c = curItem[0]
                    # ALL VALUES OF C MUST BE SHIFTED BY (B+1)
                    proxC = c - (proxyB+1)
                    
                    if len(curItem) == 1:
                        # L_ab -> N_abc
                        recStruc[proxC][0]+=1
                        
                    else:
                        # L_ab -> L_abc
                        recStruc[proxC][1].append([0,TID])                   
                    
                    
                # L"_ab -> L_abc
                for pointer,TID in struc2D[a][b][3]:
                    
                    # ALL ITEMSETS WILL HAVE ATLEAST ONE ITEM
                    curItem = DATASET[TID]  
                    
                    c = curItem[pointer+1]
                    
                    # ALL VALUES OF C MUST BE SHIFTED BY (B+1)
                    proxC = c - (proxyB+1)
                    
                    
                    if len(curItem) == pointer + 2 :
                        
                        # L"_ab -> N_abc
                        recStruc[proxC][0]+=1
                        
                    else:
                        
                        # L"_ab - L_abc
                        recStruc[proxC][1].append([pointer+1,TID])               
                
                
                # START THE RECURSION FUNCTION
                mark = recFunction(recStruc, [a, proxyB ], minSupp, nfi ,DATASET)  
                
                
                # ADD THE FREQ. ITEMS FROM THE RECURSION TO THE VARIABLE
                freq_marker.extend(mark)
                
                # empty out
                mark = []
                
                
                
            else: 
                
                # REDISTRIBUTE L_ab to L'ac and also to L_bc
                # ITERATE THROUGH THE ELEMS STORED IN L_ab
                for tid in struc2D[a][b][1]:
                    
                    curItem = DATASET[tid]
                    c = curItem[0]
                    
                    # ITEMSET ONLY HAS ONE ITEM LEFT STORED
                    # REDISTRIBUTE THIS ITEMSET TO THE FREQ. COUNT
                    if len(curItem) == 1:
                        
                        struc2D[a][c-shiftA][0] += 1
                        
                    
                        proxC = c - (proxyB+1)
    
                        struc2D[proxyB][proxC][0] += 1
                              
                    else:
                        
                        proxC = c - (proxyB+1)
                        
                        # STORE TID IN L_#_b
                        struc2D[proxyB][proxC][1].append(tid)
         
                        
                        # STORE L'_a_#
                        struc2D[a][c-shiftA][2].append(tid)
        
                        
                        # POP THE FIRST ELEMENT OFF. NO LONGER IN USE.
                        DATASET[tid] = DATASET[tid][1:]
                
                
            # EMPTY OUT L_ab
            struc2D[a][b][1] = []
    
        # CLEAR ALL OF N_a# , L_a# , L'_a#, L"_a#
        struc2D[a] = 0 




    t3=time.perf_counter()
    mineTime = t3 - t2


    itemsets = []
    
    
    # SINGLE ITEM W/ FREQ.
    for singlItem,freq in zip(sfi,ffi[idxSort]):
        
        itemsets.append([[singlItem],freq])
        
    # N-ITEM W/ FREQ.
    for prefix,freq in freq_marker:
  
        itemsets.append([sfi[prefix],freq])
    
    
    
    
    
    

    return minSupp, readTime, mineTime, nfi, itemsets

    





if __name__ == '__main__':
    
    directory = './datasets/'
    
    ### MY DATASET
    # filename = 'nTrn50_nItems7.csv'
    # file_path = os.path.join(directory, filename)
    # delimiter="," 
    # minSuppRate= 0.15
    
    
    # filename = 'nTrn100_nItems20.csv'
    # file_path = os.path.join(directory, filename)
    # delimiter="," 
    # minSuppRate= 0.20   
    
    ### KOSARAK DATASET
    # filename = 'kosarak.csv'
    # file_path = os.path.join(directory, filename)
    # delimiter=","   
    # minSuppRate = 0.002
    
    ### T40I10D100K DATASET
    # filename = 'T40I10D100K.csv'
    # file_path = os.path.join(directory, filename)
    # delimiter=","   
    # minSuppRate = 0.5
    
    
    ### RETAIL DATA DATASET
    filename = 'retailData.csv'
    file_path = os.path.join(directory, filename)
    delimiter=","   
    minSuppRate = 0.01
    
    
    t1=time.perf_counter()
    minSupp, readTime, mineTime, nsfi, itemsets = main(file_path,delimiter,minSuppRate)
    t2=time.perf_counter()
    
    totalTime = t2-t1
    
    print('-----------------------------')
    print('Summary:')
    print('-----------------------------')
    print('minSupport:',minSupp)
    print('\nData reading time:',readTime) 
    print('Mining time:      ',mineTime)
    print('Total time:       ',totalTime)
    print('') 
    print('-----------------------------')
    print('Itemset | Freq | Total:{}'.format(len(itemsets)))
    print('-----------------------------')
    
    # for itemset,freq in itemsets:
        
    #     print('{}: {}'.format(itemset,freq))
    
    # print('-----------------------------')
    
    # import csv
    # with open('new.csv', 'w', newline='') as csv_file:
    
        
    #     csv_writer = csv.writer(csv_file)
        
    #     for row in itemsets:
    #         csv_writer.writerow(row)
    
    
    
    
    
    
    
    
    
    
    
    
    
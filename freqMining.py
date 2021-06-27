
import os.path
import numpy as np
from scipy.special import comb as nCr
import time

import matplotlib.pyplot as plt


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



def main(fPath, delimiter, minSuppRate):
    '''
    Parameters:
        fName: File name of the dataset
        delimiter: what is used to seperate the data in the file
        minSuppRate: minimum support rate of accepted frequencies 
    '''

    t1 = time.perf_counter()
    
    # STORES A LIST OF 'SETS'
    # EACH ELEMENT IS A TRANSACTION WITH SOME 'LIST'
    # nItems: number of unique elements in the dataset
    DATASET , nItems = read_file(fPath,delimiter)
    
    t2 = time.perf_counter()
    
    readTime = t2 - t1
    
    # ------------------
    #  INITIALIZATION  
    # ------------------
    

    # ---------------------------------------------
    # NUMBER OF TRANSACTIONS        
    nTrans = len(DATASET)  
    
    # MINIMUM SUPPORT ( RATE * # OF TRANSACTIONS)
    minSupp = int(round(minSuppRate*nTrans,0))
    
    # ---------------------------------------------
    # SINGLE ITEM FREQUENCY ARRAY [0,1,2,......]
    # EACH INDEX IS AN 'ITEM'
    singleIF = np.zeros(nItems+1).astype(int)      

    # ADD 1 TO THE ITEM IF IT'S IN THE TRANSACTION
    for trn in DATASET:
        singleIF[trn]+=1    
    
    # LOGICAL ARRAY WHERE 1 IF ITEM'S FREQ. IS >= TO THE ACCEPTED FREQ. ELSE 0
    logicalIx = singleIF >= minSupp
    
    # STORE THE 'ITEMS' THAT HAVE A FREQUENCY > 'minSupp'
    # fi: FREQUENT ITEMS
    fI= np.where( logicalIx )[0].astype(int)

    # NUMBER OF FREQ. ITEMS
    nFI = len(fI)

    # ffi: FREQUENCY OF FREQUENT ITEMS
    ffi = singleIF[fI]
    
    # INDECES OF THE SORTED 'ffi' IN ASCENDING ORDER
    idxSort = np.argsort(ffi)  #(0: less freq )
    
    # sfi: SORTED FREQ. ITEMS
    # SORT THE FREQ. ITEMS FROM SMALLEST FREQ. TO LARGEST FREQ.
    sfi = fI[idxSort]

    # sffi: SORTED FREQUENCY OF FREQUENT ITEMS
    sffi = ffi[idxSort]
    
    # WILL BE USED IN PLACE OF THE 'fi' FOR THE ALGORITHM
    # INDEX 0 INDICATES THE SMALLEST FREQ. ITEM
    proxyIID = np.arange(0, len(fI) )    
    
    # WILL BE USED TO SELECT THE ITEMS PER TRANSACTION
    indicator = np.zeros(nItems+1,dtype=bool)

    Mtx = np.zeros( (nFI+1, nFI+1) )


    for TID,itemset in enumerate(DATASET):
        
        # GET FREQUENT ITEMS FROM CURRENT ITEMSET
        # FREQUENT ITEMS ARE SORTED BASED ON THE 'sfi'
        indicator[itemset] = 1
        logicalArray =  indicator[sfi]
        curItemset = proxyIID[logicalArray]

        if len(curItemset) > 1 :

            for ii in curItemset:
                for jj in curItemset:

                    if ii == jj:
                        break
                        
                    Mtx[ii,jj] += 1
                    
        # CLEAR THE INDICATOR FOR REUSE
        indicator[itemset] = 0   

    itemsets = [ [ [x],y ] for x,y in zip(sfi,sffi) ]

    for ii in range(Mtx.shape[0]):
        for jj in range(Mtx.shape[1]):

            if ii == jj:
                break

            if Mtx[ii,jj] >= minSupp : 
                #itemsets.append([ (ii,jj),Mtx[ii,jj] ])
                itemsets.append([ list(sfi[[ii,jj]]), Mtx[ii,jj] ])

                



    t3 = time.perf_counter()
    mineTime = t3 - t2





    return minSupp, readTime, mineTime, nFI, itemsets
    

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
    filename = 'kosarak.csv'
    file_path = os.path.join(directory, filename)
    delimiter=","   
    minSuppRate = 0.02
    
    ### T40I10D100K DATASET
    # filename = 'T40I10D100K.csv'
    # file_path = os.path.join(directory, filename)
    # delimiter=","   
    # minSuppRate = 0.01
    
    
    ### RETAIL DATA DATASET
    # filename = 'retailData.csv'
    # file_path = os.path.join(directory, filename)
    # delimiter=","   
    # minSuppRate = 0.01
    
    
    t1=time.perf_counter()
    minSupp, readTime, mineTime, nsfi, itemsets = main(file_path,delimiter,minSuppRate)
    #main(file_path,delimiter,minSuppRate)
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
    # print('-----------------------------')
    # for itemset,freq in itemsets:
    #     print('{}: {}'.format(itemset,freq))
    # print('-----------------------------')
    
    
    
    
    
    
    
    
    
    
    
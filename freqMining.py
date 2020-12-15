
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


def nextNode(curNode,pShift,minSupp,nIter,Dataset,freqBar,prefix):
    '''
    Parameter:
        curNode:
        pShift: added to the pointer to determine where in the itemset we are reading from
        minSupp: determine the cap of the frequency 
        nIter: How many items are left to iterate 
    '''

    idxDiff = len(freqBar) - nIter 

    childNode = [[] for ii in range(nIter)]
    counter = np.zeros(len(freqBar),dtype=int)

    freqItemset = []

    for TID in curNode:

        itemset, pointer = Dataset[TID]

        nItemLeft = len(itemset) - (pointer + pShift)

        if nItemLeft > 1 :

            nxtElem = itemset[ pointer + pShift ]
            childNode[nxtElem - idxDiff].append(TID)

        elif nItemLeft == 1:

            counter[itemset[-1]] += 1


    for ii,node in enumerate(childNode, start= idxDiff):

        newPrefix = prefix +  [ii]
        print('Freq.   ',newPrefix, ': ',len(node) + counter[ii])

        # ARE YOU FREQUENT?

        if len(node) + counter[ii] >= minSupp:

            newPrefix = prefix +  [ii]
            #print('Freq.   ',newPrefix, ': ',len(node) + counter[ii])

            freqItemset.append( [newPrefix,len(node) + counter[ii]] ) 

            #freqBar[ii] -= (len(node) + counter[ii])
            
            # IS THERE ENOUGH ITEMS TO CONTINUE TO THE NEXT LEVEL
            maxNumItem = np.min(freqBar[newPrefix])

            if maxNumItem >= minSupp and len(node) > 0 and len(freqBar) - ii > 0 :
                #print('NEXT LEVEL')
                freqLst = nextNode(node,pShift+1,minSupp, len(freqBar) - ii - 1,Dataset,freqBar,newPrefix)

                freqItemset.extend(freqLst)






    return freqItemset



       






def main(fPath, delimiter, minSuppRate):
    '''
    Parameters:
        fName: File name of the dataset
        delimiter: what is used to seperate the data in the file
        minSuppRate: minimum support rate of accepted frequencies
       
    '''
    
    
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

    print('MIN SUPPORT:',minSupp)
    
    ################################
    
    # SINGLE ITEM FREQUENCY ARRAY [0,1,2,......,]
    # EACH INDEX IS AN 'ITEM'
    singleIF = np.zeros(nItems+1).astype(int)      
    
    # count = 0

    # ADD 1 TO THE ITEM IF IT'S IN THE TRANSACTION
    for trn in DATASET:
        singleIF[trn]+=1    
    
    # LOGICAL ARRAY WHERE 1 IF ITEM'S FREQ. IS >= TO THE ACCEPTED FREQ. ELSE 0
    logicalIx = singleIF >= minSupp
    
    # STORE THE 'ITEMS' THAT HAVE A FREQUENCY > 'minSupp'
    # fi: FREQUENT ITEMS
    fi = np.where( logicalIx )[0].astype(int)

    # ffi: FREQUENCY OF FREQUENT ITEMS
    ffi = singleIF[fi]
    

    # INDECES OF THE SORTED 'ffi' IN ASCENDING ORDER
    idxSort = np.argsort(ffi)  #(0: less freq )
    
    # sfi: SORTED FREQ. ITEMS
    # SORT THE FREQ. ITEMS FROM SMALLEST FREQ. TO LARGEST FREQ.
    sfi = fi[idxSort]

    # sffi: SORTED FREQUENCY OF FREQUENT ITEMS
    sffi = ffi[idxSort]
    
    # WILL BE USED IN PLACE OF THE 'fi' FOR THE ALGORITHM
    # INDEX 0 INDICATES THE SMALLEST FREQ. ITEM
    proxyIID = np.arange(0, len(fi) )    
    
    # WILL BE USED TO SELECT THE ITEMS PER TRANSACTION
    indicator = np.zeros(nItems+1,dtype=bool)

    # STORE THE TID OF EACH TRANSACTION, USING THE FIRST ELEMENT
    header = [ [] for ii in range(len(fi))]

    freqBar = np.copy(sffi)


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

        if len(curItemset) > 1 :

            fElem = curItemset[0]
            header[fElem].append(TID)
            DATASET[TID] = [curItemset,0]
            
        elif len(curItemset) == 1:

            fElem = curItemset[0]
            freqBar[fElem] -= 1

        # CLEAR THE INDICATOR FOR REUSE
        indicator[itemset] = 0   


    # plt.figure(1)
    #plt.bar(range(len(sfi)),sffi)
    # plt.plot([0,len(fi)],[minSupp,minSupp])
    # plt.yscale('log')

    # plt.figure(2)
    #plt.bar(range(len(sfi)),freqBar)
    # plt.plot([0,len(fi)],[minSupp,minSupp])
    # plt.yscale('log')

    # plt.show()


    # print(len(fi))
    # print('')

    freqItemsets = []


    for idx,node in enumerate(header):
    
        if freqBar[idx] > minSupp and len(sfi) - (idx + 1) > 0:

            print('')
            print('Item:',idx,' freq:',freqBar[idx])
            print('')

            #plt.bar(range(len(freqBar)),freqBar)

            freqItemTmp = ( nextNode(node, 1 , minSupp,len(sfi) - (idx + 1),DATASET,freqBar, [idx]) )

            #freqBar[idx] -= len(freqItemTmp)

            freqItemsets.extend(freqItemTmp)

        
        for TID in node:

            itemset, pointer = DATASET[TID]
            nextPointer = (pointer+1)
            remainItems = len(itemset) - nextPointer

            if remainItems > 1 :

                fElem = itemset[nextPointer]
                #resevoir[fElem].append(TID)
                header[fElem].append(TID)
                DATASET[TID] = [itemset,nextPointer]
                
                #freqBar[itemset[pointer]] -= 1




    t3 = time.perf_counter()
    
    mineTime = t3 - t2

    totalTime = readTime + mineTime


    itemsets = []

    # SINGLE ITEM W/ FREQ.
    for singlItem,freq in zip(sfi,sffi):
        
        itemsets.append([[singlItem],freq])

        print(itemsets[-1])
        
    # N-ITEM W/ FREQ.
    for prefix,freq in freqItemsets:
  
        itemsets.append([sfi[prefix],freq])

        print(itemsets[-1])





    return totalTime, readTime, mineTime, len(sfi), itemsets



    # plt.bar(range(len(freqBar)),freqBar)  

    # plt.plot([0,len(fi)-1],[minSupp,minSupp],linestyle = '--',color = 'k')
    # plt.yscale('log')
    # #plt.legend()
    # plt.title('Number of Freq. Items:{}'.format(len(sfi)))
    # plt.show()
    


    
    

    
    

    

    





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
    minSuppRate = 0.05
    
    ### T40I10D100K DATASET
    # filename = 'T40I10D100K.csv'
    # file_path = os.path.join(directory, filename)
    # delimiter=","   
    # minSuppRate = 0.5
    
    
    ### RETAIL DATA DATASET
    # filename = 'retailData.csv'
    # file_path = os.path.join(directory, filename)
    # delimiter=","   
    # minSuppRate = 0.01
    
    
    # t1=time.perf_counter()
    main(file_path,delimiter,minSuppRate)
    # t2=time.perf_counter()
    
    # totalTime = t2-t1
    
    
    # for itemset,freq in itemsets:
        
    #     print('{}: {}'.format(itemset,freq))
    
    # print('-----------------------------')
    
    # import csv
    # with open('new.csv', 'w', newline='') as csv_file:
    
        
    #     csv_writer = csv.writer(csv_file)
        
    #     for row in itemsets:
    #         csv_writer.writerow(row)
    
    
    
    
    
    
    
    
    
    
    
    
    
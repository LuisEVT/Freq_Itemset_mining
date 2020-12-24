
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


def lvl2(L,Lp,minSupp,Dataset,prefix):

    kk = prefix[-1]

    arrSize = len(L) - prefix[-1] - 1
    childNode = [[] for ii in range(arrSize)]
    counter = np.zeros(arrSize,dtype=int)

    idxDiff = kk + 1

    for TID in L[kk]:

        itemset, pointer1 , _ = Dataset[TID]

        nItemLeft = len(itemset) - (pointer1 + 1)

        if nItemLeft > 1 :

            # THIS IS THE DATA I'M SENDING TO THE NEXT LEVELS, IF THERE IS SUCH OCCURANCE
            nxtElem = itemset[ pointer1 + 1 ]
            childNode[nxtElem - idxDiff].append(TID)

            # INCREASE POINTER BY 1
            Dataset[TID][1] += 1
            Dataset[TID][2] = Dataset[TID][1]
            L[nxtElem].append(TID)

        elif nItemLeft == 1:

            # KEEP COUNT OF THE ITEMSET, SINCE IT NO LONGER HAS MORE ELEMENTS
            # BUT I AM STILL INTERESTED IN KNOWING THE COUNT FOR THIS GIVEN SET
            counter[itemset[-1] - idxDiff ] += 1


    freqItemset = []   

    # ENSURE THAT THE SINGLE ITEMSET HAS ENOUGH SETS TO EVEN DIVE IN DEEPER
    if  len(L[kk]) + len(Lp[kk]) >= minSupp:

        print('')
        print('Item:',kk,' freq:',len(L[kk]) + len(Lp[kk]) )
        print('')

        # LOOK AT EACH OF THE RANK 2 NODES 
        # AND DETERMINE IF THEY HAVE ENOUGH SETS TO BE FREQUENT
        for ii,node in enumerate(childNode):
            
            print('')
            while(True):

                newPrefix = prefix +  [kk + 1 + ii]
                frequency = len(node) + counter[ii] + len(Lp[kk + 1 + ii])

                print('Freq.   ',newPrefix, ': ',frequency )

                if frequency  >= minSupp:

                    freqItemset.append([newPrefix,frequency])

                    freqItemset.extend( nextLevel(node,Lp,minSupp,Dataset,newPrefix) )

                    break

                sumLp = [ len(elem) for elem in Lp[:kk + 1 + ii] ]

                #print(sumLp)

                if frequency + sum(sumLp) < minSupp:
                    #print(frequency + sum(sumLp))
                    break
                
                idxMax = np.argmax(sumLp)
                for TID in Lp[idxMax]:
                    itemset, _ , pointer2 = Dataset[TID]

                    nItemLeft = len(itemset) - (pointer2 + 1)

                    if nItemLeft > 1 :

                        nxtElem = itemset[ pointer2 + 1]
                        Dataset[TID][2] += 1
                        Lp[nxtElem].append(TID)
                
                    elif nItemLeft == 1:

                        # KEEP COUNT OF THE ITEMSET, SINCE IT NO LONGER HAS MORE ELEMENTS
                        # BUT I AM STILL INTERESTED IN KNOWING THE COUNT FOR THIS GIVEN SET
                        counter[itemset[-1] - idxDiff ] += 1

                Lp[idxMax] = []


            for TID in node:
                itemset, _ , pointer2 = Dataset[TID]

                nItemLeft = len(itemset) - (pointer2 + 1)

                if nItemLeft > 1 :

                    nxtElem = itemset[ pointer2 + 1 ]
                    Dataset[TID][2] += 1
                    Lp[nxtElem].append(TID)
            
                elif nItemLeft == 1:

                    # KEEP COUNT OF THE ITEMSET, SINCE IT NO LONGER HAS MORE ELEMENTS
                    # BUT I AM STILL INTERESTED IN KNOWING THE COUNT FOR THIS GIVEN SET
                    counter[itemset[-1] - idxDiff ] += 1

            #print(counter)
            
    return freqItemset


    
def nextLevel(parent,Lp,minSupp,Dataset,prefix):

    kk = prefix[-1]

    arrSize = len(Lp) - prefix[-1] - 1
    childNode = [[] for ii in range(arrSize)]
    counter = np.zeros(arrSize,dtype=int)

    idxDiff = kk + 1

    for TID in parent:

        itemset, _ , pointer2 = Dataset[TID]
        nItemLeft = len(itemset) - (pointer2 + 1)

        if nItemLeft > 1 :

            # THIS IS THE DATA I'M SENDING TO THE NEXT LEVELS, IF THERE IS SUCH OCCURANCE
            nxtElem = itemset[ pointer2 + 1 ]
            childNode[nxtElem - idxDiff].append(TID)

            # INCREASE POINTER BY 1
            Dataset[TID][2] += 1
            childNode[nxtElem - idxDiff ].append(TID)

        elif nItemLeft == 1:

            # KEEP COUNT OF THE ITEMSET, SINCE IT NO LONGER HAS MORE ELEMENTS
            # BUT I AM STILL INTERESTED IN KNOWING THE COUNT FOR THIS GIVEN SET
            counter[itemset[-1] - idxDiff ] += 1


    freqItemset = []   

    # LOOK AT EACH OF THE RANK 2 NODES 
    # AND DETERMINE IF THEY HAVE ENOUGH SETS TO BE FREQUENT
    for ii,node in enumerate(childNode):
        
        print('')
        while(True):

            newPrefix = prefix +  [kk + 1 + ii]
            frequency = len(node) + counter[ii] + len(Lp[kk + 1 + ii])

            print('Freq.   ',newPrefix, ': ',frequency)

            if frequency  >= minSupp:

                freqItemset.append([newPrefix,frequency])

                freqItemset.extend( nextLevel(node,Lp,minSupp,Dataset,newPrefix) )

                break

            sumLp = [ len(elem) for elem in Lp[:kk + 1 + ii] ]

            if len(node) + counter[ii] + sum(sumLp) < minSupp:
                #print(len(node) + counter[ii] + sum(sumLp))
                break

            idxMax = np.argmax(sumLp)

            for TID in Lp[idxMax]:
                itemset, _ , pointer2 = Dataset[TID]

                nItemLeft = len(itemset) - (pointer2 + 1)

                if nItemLeft > 1 :

                    nxtElem = itemset[ pointer2 + 1 ]
                    Dataset[TID][2] += 1
                    Lp[nxtElem].append(TID)
            
                elif nItemLeft == 1:

                    # KEEP COUNT OF THE ITEMSET, SINCE IT NO LONGER HAS MORE ELEMENTS
                    # BUT I AM STILL INTERESTED IN KNOWING THE COUNT FOR THIS GIVEN SET
                    counter[itemset[-1] - idxDiff ] += 1

            Lp[idxMax] = []


        for TID in node:
            itemset, _ , pointer2 = Dataset[TID]

            nItemLeft = len(itemset) - (pointer2 + 1)

            if nItemLeft > 1 :

                nxtElem = itemset[ pointer2 + 1 ]
                Dataset[TID][2] += 1
                Lp[nxtElem].append(TID)
        
            elif nItemLeft == 1:

                # KEEP COUNT OF THE ITEMSET, SINCE IT NO LONGER HAS MORE ELEMENTS
                # BUT I AM STILL INTERESTED IN KNOWING THE COUNT FOR THIS GIVEN SET
                counter[itemset[-1] - idxDiff ] += 1


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
    L = [ [] for ii in range(len(fi))]
    Lp = [ [] for ii in range(len(fi))]

    print('Max Freq.: ',np.max(sffi))

    # NOTE: IN THE LOOP, THE ALGO. WILL IGNORE THE ITEMSETS 
    # THAT DO NOT HAVE THE FREQUENT SINGLE ITEMS; THE TID FOR THESE ITEMSETS WILL NOT BE RECORDED.
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
            L[fElem].append(TID)
            DATASET[TID] = [curItemset,0,0]

        # CLEAR THE INDICATOR FOR REUSE
        indicator[itemset] = 0   


    freqItemsets = []


    for idx in proxyIID:

        Lp = Lp = [ [] for ii in range(len(fi))]

        freqItemsets.extend(lvl2(L,Lp,minSupp,DATASET,[idx]))






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
  
        itemsets.append([list(sfi[prefix]),freq])

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
    
    
    
    
    
    
    
    
    
    
    
    
    
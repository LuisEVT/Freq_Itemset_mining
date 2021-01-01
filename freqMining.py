
import os.path
import numpy as np
from scipy.special import comb as nCr
import time

import matplotlib.pyplot as plt
import copy

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


def lvl2(parents,minSupp,Dataset,prefix,nFI = 10):


    kk = prefix[-1]
    arrSize = nFI - prefix[-1] - 1
    idxDiff = kk + 1

    # PACKAGES FOR THIS LEVEL
    childNode = [ [] for ii in range(arrSize)]

    # [ RESEVOIR , TOTAL COUNT IN RESEVOIR ] , [COUNT FOR EACH CHILD NODE ( WHEN ITEMSET NO LONGER HAS MORE ELEMENTS) ]
    resV = [ [ [] for ii in range(arrSize) ] , 0 ] 
    count = [ 0 for ii in range(arrSize) ] 


    for package in parents[kk]:

        TID, pointer = package
        newPointer = pointer+ 1

        itemset = Dataset[TID]
        nItemLeft = len(itemset) - newPointer

        if nItemLeft > 1 :

            # THIS IS THE DATA I'M SENDING TO THE NEXT LEVELS, IF THERE IS SUCH OCCURANCE
            nxtElem = itemset[newPointer]
            childNode[nxtElem - idxDiff].append( [ TID, newPointer] )
            parents[nxtElem].append( [ TID,newPointer] )

        elif nItemLeft == 1:

            # KEEP COUNT OF THE ITEMSET, SINCE IT NO LONGER HAS MORE ELEMENTS
            # BUT I AM STILL INTERESTED IN KNOWING THE COUNT FOR THIS GIVEN SET
            count[itemset[-1] - idxDiff ] += 1

    freqItemset = [] 

    nPackages = sum( [ len(elem) for elem in parents[kk]] )

    # ENSURE THAT THE SINGLE ITEMSET HAS ENOUGH SETS TO EVEN DIVE IN DEEPER
    if  nPackages < minSupp:
        return freqItemset


    print('')
    print('Item:',kk,' freq:',len(parents[kk]) )
    print('')

    # LOOK AT EACH OF THE RANK 2 NODES 
    # AND DETERMINE IF THEY HAVE ENOUGH SETS TO BE FREQUENT
    for ii,node in enumerate(childNode):
        

        idx = kk + 1 + ii

        print('')
        while(True):

            newPrefix = prefix +  [idx]
            frequency = len(node) + count[ii] + len(resV[0][ii])

            print('Freq.   ',newPrefix, ': ',frequency )

            if frequency  >= minSupp:

                freqItemset.append([newPrefix,frequency])

                a = copy.deepcopy(resV)
                b = count[:]

                freqItemset.extend( lvlN(node,[a],[b],minSupp,Dataset,newPrefix,nFI) )

                break

            sumLp = [ len(elem) for elem in resV[0][:ii] ]

            if frequency + sum(sumLp) < minSupp:
                #print(frequency + sum(sumLp))
                break
            

            
            idxMax = np.argmax(sumLp)

            for package in resV[0][idxMax]:

                TID, pointer = package
                itemset = Dataset[TID]
                newPointer = pointer + 1

                nItemLeft = len(itemset) - newPointer

                if nItemLeft > 1 :

                    nxtElem = itemset[ newPointer ]
                    resV[0][ nxtElem - idxDiff ].append( [ TID, newPointer ] )
            
                elif nItemLeft == 1:

                    resV[1] -= 1

                    # KEEP COUNT OF THE ITEMSET, SINCE IT NO LONGER HAS MORE ELEMENTS
                    # BUT I AM STILL INTERESTED IN KNOWING THE COUNT FOR THIS GIVEN SET
                    count[itemset[-1] - idxDiff ] += 1

            resV[0][idxMax] = []


        for package in node:

            TID, pointer = package
            itemset = Dataset[TID]
            newPointer = pointer + 1

            nItemLeft = len(itemset) - newPointer

            
            if nItemLeft > 1 :

                nxtElem = itemset[ newPointer ]
                resV[0][ nxtElem - idxDiff ].append( [ TID, newPointer ] )
                resV[1] += 1
        
            elif nItemLeft == 1:

                # KEEP COUNT OF THE ITEMSET, SINCE IT NO LONGER HAS MORE ELEMENTS
                # BUT I AM STILL INTERESTED IN KNOWING THE COUNT FOR THIS GIVEN SET
                count[itemset[-1] - idxDiff ] += 1

            
    return freqItemset


    
def lvlN(parent,Lp,count,minSupp,Dataset,prefix,nFI = 10):


    kk = prefix[-1]

    arrSize = nFI - prefix[-1] - 1
    childNode = [[] for ii in range(arrSize)]

    # RESEVOIR AND COUNT FOR THIS LEVEL
    LpN =  Lp + [ [ [ [] for ii in range(arrSize) ] , 0 ]  ]
    countN = count + [ [ 0 for ii in range(arrSize)] ]

    idxDiff = kk + 1

    for package in parent:

        TID, pointer = package
        newPointer = pointer + 1

        itemset = Dataset[TID]
        nItemLeft = len(itemset) - newPointer

        if nItemLeft > 1 :

            # THIS IS THE DATA I'M SENDING TO THE NEXT LEVELS, IF THERE IS SUCH OCCURANCE
            nxtElem = itemset[newPointer]
            childNode[nxtElem - idxDiff].append( [ TID, newPointer] )

        elif nItemLeft == 1:

            # KEEP COUNT OF THE ITEMSET, SINCE IT NO LONGER HAS MORE ELEMENTS
            # BUT I AM STILL INTERESTED IN KNOWING THE COUNT FOR THIS GIVEN SET
            countN[-1][itemset[-1] - idxDiff ] += 1


    freqItemset = []   


    # LOOK AT EACH OF THE RANK 2 NODES 
    # AND DETERMINE IF THEY HAVE ENOUGH SETS TO BE FREQUENT
    for ii,node in enumerate(childNode):

        idx = kk + 1 + ii

        print('')
        while(True):

            newPrefix = prefix +  [idx]
            frequency = len(node) + countN[-1][ii] + len(LpN[-1][0][ii]) # len(resV[0][ii])

            print('Freq.   ',newPrefix, ': ',frequency )


            if frequency  >= minSupp:

                freqItemset.append([newPrefix,frequency])
                print('--')

                a = copy.deepcopy(LpN)
                b = copy.deepcopy(countN)

                freqItemset.extend( lvlN(node,a,b,minSupp,Dataset,newPrefix) )

                break

            


            lpSums = []
            lpSumsX = []

            for yy in range(len(prefix) - 1):

                idxDiffX = (prefix[yy + 1] - prefix[yy])  # want to include it

                lpSums.append([ len(elem) for elem in LpN[yy][0][:idxDiffX ] ])
                lpSumsX.append(sum(lpSums[-1]))


            lpSums.append([ len(elem) for elem in LpN[-1][0][:ii] ])
            lpSumsX.append(sum(lpSums[-1]))



            idxMaxLp = np.argmax(lpSumsX)

            print('Node:',len(node))
            print('Rev:',len(LpN[-1][0][ii]))
            print('count:',countN[-1][ii])

            print(lpSums)
            print(lpSumsX)
            print(frequency + sum(lpSumsX))
            if frequency + sum(lpSumsX) < minSupp:
                #print(frequency + sum(sumLp))
                break



            idxMaxElem = np.argmax(lpSums[idxMaxLp])            
            print(idxMaxLp,' ',idxMaxElem)
            for package in LpN[idxMaxLp][0][idxMaxElem]:

                TID, pointer = package
                itemset = Dataset[TID]


                newPointer = pointer + 1
                nItemLeft = len(itemset) - newPointer

                if nItemLeft > 1 :

                    for xx in range( idxMaxLp, len(lpSumsX)):

                        nxtElem = itemset[ newPointer ]

                        idxDiffX =  newPrefix[xx+1] + 1

                        LpN[xx][0][nxtElem - idxDiffX].append( [ TID, newPointer ] )
            
                elif nItemLeft == 1:

                    # KEEP COUNT OF THE ITEMSET, SINCE IT NO LONGER HAS MORE ELEMENTS
                    # BUT I AM STILL INTERESTED IN KNOWING THE COUNT FOR THIS GIVEN SET

                   for xx in range( idxMaxLp, len(lpSumsX)):

                        nxtElem = itemset[ newPointer ]

                        idxDiffX =  newPrefix[xx+1] + 1

                        countN[xx][itemset[-1] - idxDiffX ] += 1



                    #LpN[idxMaxLp][1] -= 1


            LpN[idxMaxLp][0][idxMaxElem] = []



        for package in node:

            TID, pointer = package
            itemset = Dataset[TID]
            newPointer = pointer + 1

            nItemLeft = len(itemset) - newPointer

            if nItemLeft > 1 :

                nxtElem = itemset[ newPointer ]
                LpN[-1][0][nxtElem - idxDiff].append( [ TID, newPointer ] )

                # LpN[-1][1] += 1
        
            elif nItemLeft == 1:

                # KEEP COUNT OF THE ITEMSET, SINCE IT NO LONGER HAS MORE ELEMENTS
                # BUT I AM STILL INTERESTED IN KNOWING THE COUNT FOR THIS GIVEN SET
                countN[-1][itemset[-1] - idxDiff ] += 1

        #print(counter)
            
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
            L[fElem].append( [ TID, 0 ] )
            DATASET[TID] = curItemset

        # CLEAR THE INDICATOR FOR REUSE
        indicator[itemset] = 0   


    freqItemsets = []


    for idx in proxyIID:

        freqItemsets.extend( lvl2(L,minSupp,DATASET,[idx],nFI = len(fi)) )






    t3 = time.perf_counter()
    mineTime = t3 - t2


    itemsets = []

    # SINGLE ITEM W/ FREQ.
    for singlItem,freq in zip(sfi,sffi):
        
        itemsets.append([[singlItem],freq])
        
    # N-ITEM W/ FREQ.
    for prefix,freq in freqItemsets:
  
        itemsets.append([list(sfi[prefix]),freq])





    return minSupp, readTime, mineTime, len(sfi), itemsets

    


    
    

    
    

    

    





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
    # minSuppRate = 0.01
    
    
    ### RETAIL DATA DATASET
    # filename = 'retailData.csv'
    # file_path = os.path.join(directory, filename)
    # delimiter=","   
    # minSuppRate = 0.01
    
    
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

    
    for itemset,freq in itemsets:
        
        print('{}: {}'.format(itemset,freq))
    
    print('-----------------------------')
    
    
    
    
    
    
    
    
    
    
    
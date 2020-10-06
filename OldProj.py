
from numpy import *
#import pandas as pd
from matplotlib.pyplot import *
import time
import os.path




#read csv data file:
originalData=[]
nItems=1


directory = './data/'


### KOSARAK DATASET
# filename = 'kosarak.csv'
# file_path = os.path.join(directory, filename)
# delimiter=","   
# minSuppRate = 0.025

### T40I10D100K DATASET
filename = 'T40I10D100K.csv'
file_path = os.path.join(directory, filename)
delimiter=","   
minSuppRate = 0.50  


### RETAIL DATA DATASET
# filename = 'retailData.csv'
# file_path = os.path.join(directory, filename)
# delimiter=","   
# minSuppRate = 0.01



t1=time.perf_counter() #start file reading

#fName='retailData.csv'  #dataset file
#separator="," # separator between items in transaction
#minSuppRate=0.01 #assign min support rate

with open(file_path, 'r',buffering=10000000) as f: #open file, don't have to use pandas since list data type is used
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

t2=time.perf_counter() #end file reading, start mining

#Define function
def recurFn(firstCol,level,prefix):
    while prefix != []: # while prefix is not empty      
        #1. If firstCol < |F| -1
        if firstCol < len(freqItems)-1:
            #(a)
            loMx[level,(firstCol+1):]=hiMx[(level-1),(firstCol+1):]
            
            #(b) Loop through tidMx
            for s in range(loMx[(level-1),firstCol],hiMx[(level-1),firstCol]):
                t=tidMx[s,firstCol] #transaction ID        
                ptr=ptMx[s,firstCol] #pointer
                for j in range(ptr,len(originalData[t])):
                    m=originalData[t][j]
                    #itmId=originalData[t][j] #get itemId in transaction
                    #m=freqIx[itmId] #check if that item is frequent
                    #if m>=0: #if yes
                    tidMx[hiMx[(level-1),m],m]=t
                    ptMx[hiMx[(level-1),m],m]=j+1
                    if level>1:
                        ptMx[s,firstCol]=j
                    hiMx[(level-1),m]+=1
                    break
    
            #(c)
            hiMx[level,(firstCol+1):]=hiMx[(level-1),(firstCol+1):]
            
            #(d)check support
            count=hiMx[(level-1),firstCol]-loMx[(level-1),firstCol]
            #print(prefix, count)
            if count>=minSupp:
                listOfFreqItemsets.append([freqItemsSorted[prefix],count])
                #print('Count: ',count,'\t\tSet: ',freqItemsSorted[prefix])
                #ii set firstCol = firstCol+1... instead of recursive
                firstCol += 1
                level += 1
                prefix = prefix + [firstCol]
                continue
            #(e) Set firstCol +=1 instead of recursive
            firstCol += 1

            #(f)
            prefix.pop(-1) # remove last item from prefix
            #(g) Add new firstCol to prefix ( already +1 from step e)
            prefix = prefix + [firstCol]
            continue
        
        #2. Check
        count = hiMx[level -1, firstCol] - loMx[level-1, firstCol]
        #print(prefix, count)
        if  count >= minSupp:
            #print('Count: ',count,'\t\tSet: ',freqItemsSorted[prefix])
            #print(prefix)
            listOfFreqItemsets.append([freqItemsSorted[prefix],count])
        
        #3. Remove last item from prefix
        prefix.pop(-1)
        
        #4. If prefix is empty
        if prefix == []:
            break
        #5. Reach last column
        else: 
            #(a) add 1 to index of last item in prefix
            prefix[-1] +=1            #(b)
            level -= 1
            firstCol = prefix[-1]


#Create list of all items
itemsList=arange(nItems+1)
#itemsList=itemsList[1:] #delete itemID=0

#find the number of transactions:
nTrans = len(originalData)

minSupp=int(round(minSuppRate*nTrans,0))

#Create list of frequent items:
suppOfItems = array(zeros(nItems+1),dtype=int)

#Find frequent items list
for trn in originalData:
    suppOfItems[trn]+=1
freqItems = [ix for ix,x in enumerate(suppOfItems) if x>=minSupp] #get list of single freq items
freqItems = array(freqItems) ######## CT
maxItemCount = max(suppOfItems) # get max count of a single item
print('Freq items list: ',freqItems)
freqIx=-1*ones(nItems+1,dtype=int)
freqIx[freqItems]=arange(len(freqItems))

#Sort freqItems from most to least frequent
suppOfFreqItems = suppOfItems[freqItems] # get supports of each frequent item
idxSort = argsort(suppOfFreqItems)
#idxSort = idxSort[::-1] # sort indices from most to least frequent
freqItemsSorted=freqItems[idxSort] # freqItems from most to least frequent
print('item sorted list: ',freqItemsSorted)
freqIxSorted=-1*ones(nItems+1,dtype=int)
freqIxSorted[freqItemsSorted]=arange(len(freqItemsSorted))


#Create two  arrays  ptMx and tidMx
nCol=len(freqItems) # number of elements freqItems
ptMx=zeros((maxItemCount,nCol),dtype=int)
tidMx=zeros((maxItemCount,nCol),dtype=int)

#Create hiMx and loMx
hiMx=zeros((nCol,nCol),dtype=int)
loMx=zeros((nCol,nCol),dtype=int)

#Scan originalData (D) and remove non-frequent items, replace item by its index, and sort each transaction
for t, trn in enumerate(originalData):
    tmp=freqIxSorted[trn] # get index of each item in transaction from freqIx
    tmp= tmp[(tmp>=0)] # items with indices >=0 are frequent items
    tmp= sort(tmp) # sort transaction-by-indices
    originalData[t]=tmp[:] # deep copy each transaction tmp back to originalData
    if len(originalData[t]) > 0: # if transaction is not empty, divide indices among columns of tidMx
        m = originalData[t][0]
        tidMx[hiMx[0,m],m] = t #save transaction id to tidMx
        ptMx[hiMx[0,m],m] = 1 #ptMx points to the next item in the transaction
        hiMx[0,m]+=1
        

#Scan originalData and divide transaction indices in D among the columns of tidMx
#for t,trn in enumerate(originalData):
#    for j,m in enumerate(trn):
#        #m=freqIx[itm] #get index of the item in freqIx
#        #if m>=0: #if the item is a frequent item, which will have index >=0
#        tidMx[hiMx[0,m],m]=t #save transaction id to tidMx
#        ptMx[hiMx[0,m],m]=j+1 #ptMx points to the next item in the transaction
#        hiMx[0,m]+=1
#        break

#Call recurFn function with firstCol=0 and prefix = [freqItems[0]]
listOfFreqItemsets=[]
recurFn(0,1,[0])


#Finished. 
t3=time.perf_counter()

# print(listOfFreqItemsets)
#print('# of frequent itemsets:',len(listOfFreqItemsets))
print('\nData reading time:',t2-t1) 
print('Mining time:',t3-t2)
print('Total time:',t3-t1)

print('')
print('Frequent itemsets:{}'.format(len(listOfFreqItemsets)))
for itemset,count in listOfFreqItemsets:
    print(itemset,": ",count)
    
# for itemset,count in listOfFreqItemsets:
#     if len(itemset) <= 1 :
#         print(itemset,": ",count)
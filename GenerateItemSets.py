
from numpy.random import randint
import csv
import os.path
import numpy as np



# NUMBER OF TRANSACTIONS
nTrn = 50

# MAX ITEM ID
nItems = 7

# ARRAY WILL STORE TRANSACTIONS
trArray = []


# CREATE AN 'nTrn' SIZE ARRAY, WHERE ELEMENT IS A RANDOM NUMBER BETWEEN 1 AND nItems 
isr = randint(1,nItems,nTrn,dtype=int)

# DETERMINE MAX ITEMSET SIZE FOR HEADER PURPOSES
maxSize = np.max(isr)

for idx in range(nTrn):
    
    curItemsetSize = isr[idx]
    
    # CREATE A ZERO LIST OF SIZE 'isr[idx])'
    arr = [0 for kk in range(curItemsetSize)]
    
    # FILL THE ARRAY WILL RANDOM NUMBERS
    for ii in range(curItemsetSize):
        arr[ii] =  randint(1,10)

    # APPEND ITEMSET INTO THE TRANSACTION ARRAY
    trArray.append(arr)

# CREATE A HEADER
heading = [ kk for kk in range(1,maxSize+1)]



directory = './data/'
filename = 'nTrn{}_nItems{}.csv'.format(nTrn,nItems)
file_path = os.path.join(directory, filename)

# STORE THE LIST INTO A CSV FILE
with open(file_path, "w", newline="") as f:
    writer = csv.writer(f,delimiter=',')
    writer.writerow(heading)
    writer.writerows(trArray)




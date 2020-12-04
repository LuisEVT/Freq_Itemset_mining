
import csv
import os.path
from numpy.random import randint
import numpy as np


def convertToCSV(filename,delimeter, directory='./'):
    '''
    Parameter:
        filename: File name
        delimeter: The delimeter of file
        directory: Directory where the file is located.

    Output:
        Creates a .csv file with the same filename
    '''

    file_path1 = os.path.join(directory, filename1)

    ## WRITE AS .CSV
    #filename2 = 'kosarak.csv'
    filename2 = 'T40I10D100K.csv'
    file_path2 = os.path.join(directory, filename2)

    with open(file_path1) as dat_file, open(file_path2, 'w', newline='') as csv_file:
        
        csv_writer = csv.writer(csv_file)
        
        for line in dat_file:
            
            row = [item.strip() for item in line.split(' ')]
            csv_writer.writerow(row)



def generateItemset(nItems,nTrn,lenTrn, directory = './'):
    '''
    Parameter:
        nItems: Max Item ID ( must be > 1)
        nTrn: Number of transactions
        lenTrn: max Length of each transaction ( Must be <= nItems)

    Output:
        Create a .csv file with 'nTrn' transactions
    '''

    # ARRAY WILL STORE TRANSACTIONS
    trArray = np.zeros(nTrn)
    # LIST OF VALUES FROM 1 TO MAX ITEM ID
    sample = np.arange(1,nItems)

    # LOOP THROUGH EACH TRANSACTION AND GENERATE ITEMSETS
    for ii in range(len(trArray)):

        # RANDOM ITEMSET SIZE
        size = np.random(1,lenTrn,dtype = int)

        # GENERATE ITEMSET (IN ORDER)
        trArray[ii] = np.sort( np.random.sample(sample,size) )


    filename = 'nTrn{}_nItems{}.csv'.format(nTrn,nItems)
    file_path = os.path.join(directory, filename)

    # STORE THE LIST INTO A CSV FILE
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f,delimiter=',')
        writer.writerows(trArray)




if __name__ == "__main__":

    # CONVERTING .DAT FILE TO .CSV
    # directory = './data/'
    # filename = 'T40I10D100K.dat'
    # delimeter = ' '
    # convertToCSV(filename,delimeter, directory)

    # GENERATE A DATASET FILE 
    directory = './data/'
    nItems = 10
    nTrn = 50
    lenTrn = 6
    generateItemset(nItems,nTrn,lenTrn,directory)












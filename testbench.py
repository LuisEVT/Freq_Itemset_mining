# -*- coding: utf-8 -*-

from freqMining import main
import os.path
import time
import pandas as pd
from datetime import datetime

import matplotlib.pyplot as plt



def datasetTestbench(filename, delimiter, minSuppRateLst, directory ='./'):
    '''
    Parameter:
        filename: Name of the file with transactions
        delimter: Delimeter that seperates each itemset in each transaction
        minSuppRateLst: A list of (0-1) rates that state the minimal support rate for the frequency of the itemset
        directory: where the file is located
    '''



    column_names = ['File',
                'minSuppRate',
                'readTime',
                'mineTime',
                'runtime',
                'nSingleFreqItem',
                'nFreqItem']

    df = pd.DataFrame(columns = column_names)

    df = df.astype({'File':'string',
                    'minSuppRate':'int64',
                    'readTime':'float64',
                    'mineTime':'float64',
                    'runtime':'float64',
                    'nSingleFreqItem':'int64',
                    'nFreqItem':'int64'})


    path = os.path.join(directory, filename)

    for ii,minSuppRate in enumerate(minSuppRateLst):

        print('RUN: {} out of {}'.format(ii+1,len(minSuppRateLst)))

        try:
            t1=time.perf_counter()
            _, readTime, mineTime, nsfi, itemsets = main(path,delimiter,minSuppRate)
            t2=time.perf_counter()
            
            totalTime = t2-t1
            
            df = df.append({'File': filename,
                            'minSuppRate':minSuppRate,
                            'readTime':readTime,
                            'mineTime':mineTime,
                            'runtime':totalTime,
                            'nSingleFreqItem':nsfi,
                            'nFreqItem':len(itemsets) },ignore_index = True)

        except:

            df = df.append({'File': filename,
                            'minSuppRate':minSuppRate,
                            'readTime':0,
                            'mineTime':0,
                            'runtime':0,
                            'nFreqItem':0 },ignore_index = True)


    ######################################
    ### SAVE RAW PANDA DATAFRAME AS CSV FILE 
    #####################################
            
    directory1 = './TestbenchData/'

    filename = '{}Data.csv'.format(filename[:-4])

    file_path = os.path.join(directory1, filename)

    if not os.path.isdir(directory1):
        os.mkdir(directory1)

    df.to_csv(file_path)


def plot(filename,directory='./TestbenchData'):

    ### File Location
    file_path = os.path.join(directory, filename)
    df = pd.read_csv(file_path)

    plt.plot(df['minSuppRate'], df['mineTime'])

    plt.xlabel('Min. Support Rate')
    plt.ylabel('Mining Time (sec)')
    plt.title('{} Dataset'.format(filename[:-8]))

    plt.show()




if __name__ == '__main__':

    directory = './datasets/'

    ### KOSARAK DATASET
    # filename = 'kosarak.csv'
    # delimiter=","   
    # minSuppRateLst = [0.06, 0.07, 0.08, 0.09, 0.1] 
    # datasetTestbench(filename, delimiter, minSuppRateLst, directory)

    #plot(filename = 'kosarakData.csv',directory='./TestbenchData')


    ### T40I10D100K DATASET
    # filename = 'T40I10D100K.csv'
    # delimiter=","   
    # minSuppRateLst = [0.1, 0.2, 0.3, 0.4, 0.5]
    # datasetTestbench(filename, delimiter, minSuppRateLst, directory)

    # plot(filename = 'T40I10D100KData.csv',directory='./TestbenchData')
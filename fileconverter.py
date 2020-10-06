




import csv
import os.path


directory = './data/'

# DATA AS .DAT
#filename1 = 'kosarak.dat'
filename1 = 'T40I10D100K.dat'
file_path1 = os.path.join(directory, filename1)
delimiter=" "   

## WRITE AS .CSV
#filename2 = 'kosarak.csv'
filename2 = 'T40I10D100K.csv'
file_path2 = os.path.join(directory, filename2)



with open(file_path1) as dat_file, open(file_path2, 'w', newline='') as csv_file:
    
    csv_writer = csv.writer(csv_file)
    
    for line in dat_file:
        
        row = [item.strip() for item in line.split(' ')]
        csv_writer.writerow(row)
        
        
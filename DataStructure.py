







def dataStruc(nItems = 5 , maxSubset = 3):
    
    
    
    item = 0
    
    struc = []
    
    
    for nElem in range(nItems + 1,maxSubset ,-1):
        
        
        lvlArray = [item for kk in range(nElem)]
        
        struc.append(lvlArray)
        
    
    return struc
    
    
    

a = dataStruc( nItems = 5, maxSubset = 3)


for lvl in a :
    print(lvl)
    
    
    
print(a)


































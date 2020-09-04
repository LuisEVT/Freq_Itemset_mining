     
     
for ii in range(5):
    for jj in range(ii):   
        for kk in range(jj):
              
        
            print(ii-2,jj-1,kk)
  
print('')
    
 
# FURTHER TESTING IS REQUIRED
# BUT, IT SEEMS TO WORK 

def create_freq_itemsetList( nItems = 5, nLvl = 3, store = int):

    nBase = (nItems - nLvl +1)
    
    

    if nLvl==1 and store == int:
        return [0 for x in range(nBase) ]
    elif nLvl== 1 and store == list:
        return [[] for x in range(nBase)]
    

    if nLvl > 1 :
        
        base = [ []  for x in range(nBase)] # lvl 1
        
        
        for idx in range(0,nBase):
            
            b = 0
            
            if store == list :
                b = []
            
           
            for lvl in range(1 , nLvl):
                
                b = b * (idx+1)
                b = [b]
                
                #print('b:',b)
            #print('')
            
            
            
            for x in range(idx,nBase):
            
                base[x].extend(b[:])

    return base



a = create_freq_itemsetList( nItems = 5, nLvl = 3, store = int)
print('')
for elem in a:
    print(elem)


print('')
#print(a[5-2][3-1])
    
#print('')
#print(a[5-3][4-2][3-1])
#print(a[5-4][4-3][3-2][2-1])   
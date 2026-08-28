## Working code for linking functions to datasets on local systems. 
## this has been added to C:/Python3/Lib/ directory
## This will be superseeded by test dataset which will be published in due course. 


import sys
#Ultra test set - includes dicom images for heel and forefoot from 2 ultrasound probe types. 
ultra_test = 'C:/Users/hls376/OneDrive - University of Salford/Code/[Data]_PYData/Tracker_TestSet'
    
def ultra_point():
    return ultra_test

'''
# sys.path.append(ultra_test)

print()
print('Paths Added:')
print('	' + ultra_test)
print() 
print('Callable Paths:')
print('        Ultra Test:-        ultra_point()	') 
print() 

'''


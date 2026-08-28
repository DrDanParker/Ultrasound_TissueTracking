import os
import pandas as pd




########################################################


d_path = 'C:/Users/hls376/University of Salford/Ultrasound in Diabetes - General/Pilot/Data/DICOM/Diabetes Group'
j_path = 'C:/Users/hls376/University of Salford/Ultrasound in Diabetes - General/Pilot/Data/JPEGS/Diabetes Group'


folderlist = os.listdir(d_path)
print(folderlist)

'''
# d_path = 'E:/ND101/DICOM/'
# j_path = 'E:/ND101/JPEG/'

o_path = 'E:/ND101/output/'

DICOM = os.listdir(d_path)
JPEG = os.listdir(j_path)
# print(len(JPEG))

flist = pd.read_excel('E:/ND101/NameList.xlsx',sheet_name='ND101',names=['jpeg','fname','notes'])
print(flist['fname'][10])

'''


'''
for i in range(0,40):
    print(JPEG[i])
    BaseName, o_ext = os.path.splitext(JPEG[i])

    print(DICOM[i])
    
    print(flist['fname'][i])
    
    os.rename(d_path+DICOM[i],o_path+flist[i])
    os.rename(d_path+JPEG[i],o_path+flist[i]+o_ext)


'''    
    
    
    
    
    
'''


print(len(DICOM))
print(len(flist))

if len(DICOM) == len(flist):
    for i in range(0,len(DICOM)):
        print(DICOM[i])
        print(flist[i])
        os.rename(d_path+DICOM[i],o_path+flist[i])





# os.rename(oldfile, newfile)

'''
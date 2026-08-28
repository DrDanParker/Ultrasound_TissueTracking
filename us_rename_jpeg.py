import os
import pandas as pd
import xarray as xr
import pydicom as dicom
import matplotlib.pylab as plt
import matplotlib.image as mpimg


########################################################

### Done for Diab to 109 - however 109 had wrong label used ND instead of DB. check with Jen. 
### Done for Non Diab to 115 

# j_path = 'C:/Users/User/University of Salford/Ultrasound in Diabetes - General/Pilot/Data/JPEGS/Non-Diabetic Group/'

j_path = 'C:/Users/User/University of Salford/Ultrasound in Diabetes - Documents/General/Pilot/Data/JPEGS/Pre-Diabetic group/'

folder_list = os.listdir(j_path)
print(folder_list)

for folder in folder_list:
    JPEG = os.listdir(j_path + folder + '/')
    s_name = folder[:-5]
    print(s_name)
    flist = pd.read_excel('C:/Users/User/University of Salford/Ultrasound in Diabetes - Documents/General/Pilot/Data/File naming_Current.xlsx',sheet_name=s_name)
    I_files = flist[flist.columns[0]]
    O_files = flist[flist.columns[1]]
    
    print('Index:',len(I_files))
    print('JPEG:',len(JPEG))

    for i in range(0,len(I_files)):
        ref = I_files[i]

        for j in range(0,len(JPEG)):
            j_base, j_ext = os.path.splitext(JPEG[j])
            if ref == j_base:
                print(ref,JPEG[j],O_files[i])

                # os.replace(j_path+folder+'/'+JPEG[j],j_path+folder+'/'+O_files[i]+j_ext)
        


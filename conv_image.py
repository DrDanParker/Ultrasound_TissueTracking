#########################################################
#
#  Ultrasound Dataset Tools
#	For processing and labelling diacom files 
#	Uses XArray to build 2d stacked grid per participant
#
#	Author D Parker - University of Salford - Nov 23
#
#########################################################


import os
import xarray as xr
import pydicom as dicom
import matplotlib.pylab as plt


def batch_load(data_path):
    """load xarray data"""
    # files = os.listdir(data_path)
    # files = [os.path.splitext(file)[0] for file in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, file))]

    files = [file for file in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, file)) and '.' not in file]

    print(files)
    print('importing files:')

    for i in range(len(files)):
        ds = dicom.dcmread(data_path + files[i])
        try:
            ds.ActualFrameDuration
            # ps = ds.pixel_array
        
        except:
            
            if not os.path.exists(data_path + files[i] +'_RAW.jpeg'):
                
                print(files[i])

                ps = ds.pixel_array
                da = xr.DataArray(data=ps,dims=['d','w','l'],name=ds.PatientName, attrs={'ImageType':ds.ImageType}) # Add more attributes as needed
                
                # f_name = data_path + 'Image' + files[i] + 'RAW.jpeg'

                plt.imshow(ps)
                plt.savefig(data_path + files[i] +'_RAW.jpeg')
                
                plt.imshow(da[130:800,400:1050])
                plt.savefig(data_path + files[i] +'_CROPPED.jpeg')
                

                # plt.figure()
                # plt.subplot(211)
                # plt.imshow(ps)
                # plt.subplot(212)
                # plt.imshow(da[130:800,400:1050])
                # plt.show()

          

################################################################################
### RUN CODE
################################################################################

# specify your image path
# image_path = 'C:/Users/hls376/University of Salford/Ultrasound in Diabetes - General/Pilot/2023 - October/25.10.23/__110336'
db_path = 'C:/Users/hls376/University of Salford/Ultrasound in Diabetes - General/Pilot/Data/Stage 2/DICOM/'


folders = next(os.walk(db_path))[1]
print(folders)

for folder in folders:
    i_path  = db_path + folder + '/'
    batch_load(i_path)
    print(i_path)
# batch_load(image_path)


#### NOTES
# print(ds.dir()) # diacom meta tags

import xarray as xr
# from netCDF4 import Dataset
import numpy as np
import os
import pydicom
import matplotlib.pylab as plt
from PIL import Image


def build_dataset(file_name): # dataset = folder/dataset.nc
    if not os.path.exists(file_name):
        # Create a new NetCDF file
        with nc.Dataset(file_name, 'w', format='NETCDF4') as ds:
            # Define dimensions
            depth = ds.createDimension('d', None)
            width = ds.createDimension('w', None)
            layer = ds.createDimension('l', None)
            
            # Define variables
            depths = ds.createVariable('time', np.float64, ('depth',))
            widths = ds.createVariable('lat', np.float64, ('width',))
            layers = ds.createVariable('lon', np.float64, ('layer',))
            
        print(f"Created NetCDF file {file_name}")
    else:
        print(f"NetCDF file {file_name} already exists. Skipping creation.")

'''
def add_to_dataset(folder, dataset):
    # Open the NetCDF file
    
    d = Dataset(dataset, 'a')
    dt = d.variables['files'] #required dimension
    data = d.variables['x_array'] # required data

    # Add the numpy array to a slice
    data[len(dt):len(dt) + 1, :, :] = <some data>

    # Add the extra time step
    dt[len(dt) - 1] = date2num(datetime(2024, 5, 29), dt.units)

    # Close the NetCDF file
    d.close()
'''




def load_dicom(fpath,folder):

    output = {}
    flist = os.listdir(fpath + folder)
    # flist = flist[:10]
    ## need test to find out if an existing nc file is there
    if folder + '_d_to_x.nc' in flist:
        print('d_to_x file exists for:' + folder)
    else:
        for filename in flist:
            image_path = os.path.join(folder, filename)
            print('importing: ' + filename)
            if '.nc' not in filename:
                if os.stat(image_path).st_size < 10485760:
                    ds = pydicom.dcmread(image_path)
                    ps = ds.pixel_array
                    da = xr.DataArray(data=ps.astype(int),dims=['d','w','l'],name=filename)
                    c_da = da[125:780,400:1050]
                    c_da.plot.imshow()
                    output[filename] = c_da
        plt.show()
        ds = xr.Dataset(output)
        ds.to_netcdf(folder + '/d_to_x.nc')
        print('data exported to: ' + folder + '/' + folder + '_d_to_x.nc') 

### Set Directory::
main_path = 'C:/Users/User/University of Salford/Ultrasound in Diabetes - Documents/General/Pilot/Data/DICOM/'
diab_path = 'Diabetes Group/'

#pre_path =
#non_path = 

f_path = main_path + diab_path

print(f_path)
print(f_path.split('/'))

dirs = f_path.split('/')
print(dirs[:-2].join('/'))

folder_list = os.listdir(f_path)
print(folder_list)



'''



fname = f_path + 'example.nc'
build_dataset(fname)

'''
'''
folder_list = os.listdir(f_path)
for folder in folder_list:
    load_dicom(f_path, folder)
'''

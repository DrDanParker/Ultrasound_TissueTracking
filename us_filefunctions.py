#########################################################
#
#  Ultrasound Dataset Tools
#	us_filefunctions - cross script functions for data handling  
#
#	Author D Parker - University of Salford - Sept 26
#
#########################################################

import os
import pydicom
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
# from netCDF4 import Dataset


def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.144])

def load_dat(dicom_file): # Loads dicom file, converts to pixel array and returns cropped data focused on image frame. 
    
    ds = pydicom.dcmread(dicom_file)
    px = ds.pixel_array
    gx = rgb2gray(px)

    # Convert the new array to a DataArray
    da = xr.DataArray(gx, dims=['x', 'y'],name=ds.PatientName)
    #  attrs={'ImageType':ds.ImageType}) # Add more attributes as needed

    # Crop for system settings 
    # System is GE 
    cropped = np.array(da[130:800,200:1200])

    # plt.figure()
    # plt.imshow(da)

    # cropped = da[130:800,200:1200]
    # plt.figure()
    # plt.imshow(cropped)
    # plt.show()

    return(da, cropped)

def dicom_meta(dicom_file):

    # Load the DICOM file
    ds = pydicom.dcmread(dicom_file)

    metadata = {elem.name: str(elem.value) for elem in ds}
    df = pd.DataFrame([metadata])

    # df.to_excel(data_path + "full_dicom_metadata.xlsx", index=False)
    for tag in df.keys():
        print(tag + '  : ' + df[tag])
    break

    '''
    # Define a list of common metadata tags to extract
    tags_to_extract = [
        "PatientName", "PatientID", "PatientBirthDate", "PatientSex",
        "StudyDate", "StudyTime", "StudyDescription", "Modality",
        "SeriesDescription", "InstitutionName", "Manufacturer",
        "ReferringPhysicianName", "BodyPartExamined", "ProtocolName"
    ]

    # Extract available metadata
    metadata = {}
    for tag in tags_to_extract:
        value = getattr(ds, tag, "N/A")
        metadata[tag] = str(value)

    # Convert to DataFrame
    df = pd.DataFrame([metadata])

    # Save to Excel
    output_path = "dicom_metadata.xlsx"
    df.to_excel(output_path, index=False)

    print(f"Metadata saved to {output_path}")
    '''

'''
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

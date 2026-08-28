import xarray as xr
import numpy as np
import matplotlib.pylab as plt

#ofile = 'D:/ND101/DICOM/Diabetes Group/DB101/d_to_x.nc'

main_path = 'C:/Users/User/University of Salford/Ultrasound in Diabetes - Documents/General/Pilot/Data/DICOM/'
diab_path = 'Diabetes Group/DB101/'

ofile = main_path + diab_path + 'd_to_x.nc'

ds = xr.open_dataset(ofile)

for f in ds.data_vars:
    da = ds[f]

    plt.figure()
    da.plot.imshow()

plt.show() 
